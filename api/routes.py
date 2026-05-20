import time
import uuid
from fastapi import APIRouter
from agents.orchestrator import app
from agents.state import DermaFlowState
from api.schemas import ChatRequest, ChatResponse, SourceChunk
from api.session import create_session, get_session, save_session
from config import config

router = APIRouter()


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

    session_id = request.session_id or str(uuid.uuid4())
    create_session(session_id)

    initial_state: DermaFlowState = {
        "query": request.query,
        "condition": request.condition_hint,
        "image_path": None,
        "session_id": session_id,
        "history": get_session(session_id).get("history", []),
        "intent": None,
        "retrieved_chunks": [],
        "response": "",
        "agent_used": "",
        "confident": False,
        "error": None
    }

    output = app.invoke(initial_state)
    answer = output.get("response", "")

    session = get_session(session_id)
    history = session.get("history", [])
    history.append({"role": "user",      "content": request.query})
    history.append({"role": "assistant", "content": answer})

    save_session(session_id, {"history": history})

    latency_ms = round((time.time() - start_time) * 1000, 2)

    sources = [
        SourceChunk(
            source    = c.get("source",    "unknown"),
            condition = c.get("condition", "unknown"),
            score     = c.get("score",     0.0),
            preview   = c.get("text",      "")[:120]
        )
        for c in output.get("retrieved_chunks", [])
    ]

    return ChatResponse(
        session_id = session_id,
        response   = answer,
        agent_used = output.get("agent_used", ""),
        sources    = sources,
        confident  = output.get("confident", False),
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

