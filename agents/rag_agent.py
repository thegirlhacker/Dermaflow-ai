from agents.state import DermaFlowState
from config import config
from rag.retriever import retrieve
from utils.prompts import RAG_RESPONSE_PROMPT
import google.generativeai as genai
import logging
import time

logger = logging.getLogger("rag_agent")
genai.configure(api_key=config.GEMINI_API_KEY)


def build_rag_prompt_str(
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
            f"{'User' if h.get('role') == 'user' else 'Assistant'}: {h.get('content')}"
            for h in history
        ]
        history_text = "Conversation so far:\n" + "\n".join(turns) + "\n"

    return RAG_RESPONSE_PROMPT.format(
        history=history_text,
        context=context,
        query=query
    )


class RAGAgent:
    def __init__(self, model: genai.GenerativeModel, retrieve_fn):
        self.model = model
        self.retrieve_fn = retrieve_fn

    def __call__(self, state: DermaFlowState) -> DermaFlowState:
        start_time = time.time()
        logger.info("RAG agent started | session=%s", state.get("session_id"))
        
        history = state.get("history", [])
        
        # Metadata filtering logic
        condition = state.get("condition")
        intent = state.get("intent")
        
        result = self.retrieve_fn(
            query=state["query"],
            condition=condition,
            intent=intent
        )

        if not result["confident"]:
            latency = (time.time() - start_time) * 1000
            logger.info("RAG retrieval low confidence, routing to fallback | latency=%.2fms", latency)
            return {
                **state,
                "retrieved_chunks": result["chunks"],
                "agent_used": "rag_agent",
                "confident": False,
                "latency_ms": latency
            }

        prompt = build_rag_prompt_str(
            query=state["query"],
            chunks=result["chunks"],
            history=history[-3:] if history else []
        )

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
        except Exception as e:
            logger.error("RAG Gemini generation failed: %s", e)
            error_msg = str(e).lower()
            if "429" in error_msg or "quota" in error_msg:
                response_text = "Sorry, I hit a rate limit with the AI provider. Please wait a few seconds and try again."
            elif "block" in error_msg or "safety" in error_msg:
                response_text = "Sorry, the response was blocked by the safety filters."
            else:
                response_text = "Sorry, I encountered an error while generating the response."
            
        latency = (time.time() - start_time) * 1000
        logger.info("RAG agent complete | confident=True | latency=%.2fms", latency)

        return {
            **state,
            "response": response_text,
            "retrieved_chunks": result["chunks"],
            "agent_used": "rag_agent",
            "confident": True,
            "latency_ms": latency,
            "error": None
        }

# Instantiate with dependencies injected
_model = genai.GenerativeModel(config.LLM_MODEL)
rag_agent = RAGAgent(model=_model, retrieve_fn=retrieve)
