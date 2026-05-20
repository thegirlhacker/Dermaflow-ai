import time
import uuid
from fastapi import APIRouter
from api.schemas import ChatRequest, ChatResponse, SourceChunk
from api.session import create_session, get_session, save_session
from rag.retriever import retrieve
from config import config
import google.generativeai as genai

router = APIRouter()

genai.configure(api_key=config.GEMINI_API_KEY)

# ─────────────────────────────────────────────
# helper — build RAG prompt
# ─────────────────────────────────────────────

def build_rag_prompt(
    query: str,
    chunks: list[dict],
    history: list[dict]   # history WITHOUT current query — pass history[:-1]
) -> str:

    # include source label so LLM can cite it
    context = "\n\n".join([
        f"[Source: {c.get('source', 'unknown')} | Condition: {c.get('condition', 'unknown')}]\n{c['text']}"
        for c in chunks
    ])

    # last 3 turns before current query — avoids duplication
    history_text = ""
    if history:
        turns = [
            f"{'User' if h['role'] == 'user' else 'Assistant'}: {h['content']}"
            for h in history
        ]
        history_text = "\n".join(turns)

    return f"""You are DermaFlow AI, a dermatology assistant.
Answer ONLY using the medical context provided below.
If context is insufficient, say so clearly.
Always end with: "This is for informational purposes only and not a medical diagnosis."

{f"Conversation so far:{chr(10)}{history_text}{chr(10)}" if history_text else ""}
Medical Context:
{context}

User Question: {query}

Answer:"""


# ─────────────────────────────────────────────
# new session
# ─────────────────────────────────────────────

@router.post("/new-chat")
async def new_chat():
    session_id = str(uuid.uuid4())
    create_session(session_id)
    return {"session_id": session_id}


# ─────────────────────────────────────────────
# main chat endpoint
# ─────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    start_time = time.time()

    # load session
    session = get_session(request.session_id)
    history = session.get("history", [])

    # retrieve BEFORE appending current query to history
    # so history passed to prompt is only previous turns
    result = retrieve(
        query=request.query,
        condition=request.condition_hint
    )

    if not result["confident"]:
        answer     = (
            "I could not find enough relevant medical information for this query. "
            "Please try rephrasing or select a specific condition."
        )
        agent_used = "fallback_agent"

    else:
        # pass history WITHOUT current query to avoid duplication in prompt
        prompt = build_rag_prompt(
            query=request.query,
            chunks=result["chunks"],
            history=history[-3:] if history else []
        )

        model    = genai.GenerativeModel(config.LLM_MODEL)
        response = model.generate_content(prompt)
        answer   = response.text
        agent_used = "rag_agent"

    # NOW append both turns to history after generation
    history.append({"role": "user",      "content": request.query})
    history.append({"role": "assistant", "content": answer})

    save_session(request.session_id, {"history": history})

    latency_ms = round((time.time() - start_time) * 1000, 2)

    sources = [
        SourceChunk(
            source    = c.get("source",    "unknown"),
            condition = c.get("condition", "unknown"),
            score     = c.get("score",     0.0),
            preview   = c.get("text",      "")[:120]
        )
        for c in result["chunks"]
    ]

    return ChatResponse(
        session_id = request.session_id,
        response   = answer,
        agent_used = agent_used,
        sources    = sources,
        confident  = result["confident"],
        latency_ms = latency_ms
    )


# ─────────────────────────────────────────────
# health check
# ─────────────────────────────────────────────

@router.get("/health")
async def health():
    try:
        from rag.vectordb import index
        stats = index.describe_index_stats()
        return {
            "status":       "ok",
            "vectors":      stats.total_vector_count,
            "model":        config.LLM_MODEL
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}

