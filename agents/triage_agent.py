import logging

from agents.state import DermaFlowState
from config import config
from utils.prompts import TRIAGE_PROMPT
import google.generativeai as genai

logger = logging.getLogger("triage_agent")

genai.configure(api_key=config.GEMINI_API_KEY)

VALID_INTENTS = {
    "condition_info",
    "ingredient",
    "web_search",
    "image"
}

class TriageAgent:
    def __init__(self, model: genai.GenerativeModel):
        self.model = model

    def __call__(self, state: DermaFlowState) -> DermaFlowState:
        import time
        start_time = time.time()
        
        logger.info(
            "Triage started | session=%s query='%s'",
            state.get("session_id", "unknown"),
            state.get("query", "")
        )

        query = state.get("query", "").lower()

        if state.get("image_path"):
            logger.info("Image provided, forcing 'image' intent.")
            return {
                **state,
                "intent": "image",
                "latency_ms": (time.time() - start_time) * 1000
            }
            
        # Rule-based checks
        ingredient_keywords = ["ingredient", "retinol", "aha", "bha", "salicylic", "niacinamide", "vitamin c", "acid"]
        web_keywords = ["latest", "news", "research", "trending"]
        
        if any(kw in query for kw in ingredient_keywords):
            logger.info("Ingredient keyword detected, setting 'ingredient' intent.")
            return {
                **state,
                "intent": "ingredient",
                "latency_ms": (time.time() - start_time) * 1000
            }
            
        if any(kw in query for kw in web_keywords):
            logger.info("Web search keyword detected, setting 'web_search' intent.")
            return {
                **state,
                "intent": "web_search",
                "latency_ms": (time.time() - start_time) * 1000
            }

        # Gemini fallback
        try:
            response = self.model.generate_content(
                TRIAGE_PROMPT.format(query=state.get("query", ""))
            )
            intent = response.text.strip().lower()
        except Exception as e:
            logger.error(f"Error during triage generation: {e}")
            intent = "condition_info"

        if intent not in VALID_INTENTS:
            intent = "condition_info"

        latency = (time.time() - start_time) * 1000
        logger.info("Intent detected = %s | method=gemini_fallback | latency=%.2fms", intent, latency)

        return {
            **state,
            "intent": intent,
            "latency_ms": latency
        }

# Instantiate with dependencies injected
_model = genai.GenerativeModel(config.LLM_MODEL)
triage_agent = TriageAgent(model=_model)
