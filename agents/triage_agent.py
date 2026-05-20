import logging

from agents.state import DermaFlowState
from config import config
import google.generativeai as genai

logger = logging.getLogger("triage_agent")

genai.configure(api_key=config.GEMINI_API_KEY)


TRIAGE_PROMPT = """
You are a query classifier for a dermatology assistant called DermaFlow.

Classify the user query into exactly ONE of these intents:

condition_info
ingredient
web_search
image

Query: {query}

Reply with ONLY the intent label.
"""


VALID_INTENTS = {
    "condition_info",
    "ingredient",
    "web_search",
    "image"
}


def triage_agent(state: DermaFlowState) -> DermaFlowState:

    logger.info(
        "Triage started | session=%s query='%s'",
        state["session_id"],
        state["query"]
    )

    model = genai.GenerativeModel(
        "gemini-1.5-flash"
    )

    response = model.generate_content(

        TRIAGE_PROMPT.format(
            query=state["query"]
        )
    )

    intent = response.text.strip().lower()

    if intent not in VALID_INTENTS:
        intent = "condition_info"

    logger.info(
        "Intent detected = %s",
        intent
    )

    return {
        **state,
        "intent": intent
    }