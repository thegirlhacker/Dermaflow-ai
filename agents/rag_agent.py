from agents.state import DermaFlowState
from config import config
from rag.retriever import retrieve
import google.generativeai as genai


genai.configure(api_key=config.GEMINI_API_KEY)


def build_rag_prompt(
    query: str,
    chunks: list[dict],
    history: list[dict]
) -> str:
    context = "\n\n".join([
        f"[Source: {c.get('source', 'unknown')} | Condition: {c.get('condition', 'unknown')}]\n{c['text']}"
        for c in chunks
    ])

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


def rag_agent(state: DermaFlowState) -> DermaFlowState:
    history = state.get("history", [])

    result = retrieve(
        query=state["query"],
        condition=state.get("condition")
    )

    if not result["confident"]:
        return {
            **state,
            "response": (
                "I could not find enough relevant medical information for this query. "
                "Please try rephrasing or select a specific condition."
            ),
            "retrieved_chunks": result["chunks"],
            "agent_used": "fallback_agent",
            "confident": False,
            "error": None
        }

    prompt = build_rag_prompt(
        query=state["query"],
        chunks=result["chunks"],
        history=history[-3:] if history else []
    )

    model = genai.GenerativeModel(config.LLM_MODEL)
    response = model.generate_content(prompt)

    return {
        **state,
        "response": response.text,
        "retrieved_chunks": result["chunks"],
        "agent_used": "rag_agent",
        "confident": True,
        "error": None
    }
