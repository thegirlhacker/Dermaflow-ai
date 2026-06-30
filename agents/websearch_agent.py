import logging
import time

import google.generativeai as genai
from tavily import TavilyClient

from agents.state import DermaFlowState
from config import config

from utils.query_builder import build_search_query
from websearch.formatter import format_results
from utils.prompts import WEBSEARCH_RESPONSE_PROMPT


logger = logging.getLogger("websearch_agent")

genai.configure(
    api_key=config.GEMINI_API_KEY
)

tavily = TavilyClient(
    api_key=config.TAVILY_API_KEY
)


class WebSearchAgent:
    def __init__(self, model: genai.GenerativeModel, tavily_client: TavilyClient):
        self.model = model
        self.tavily_client = tavily_client

    def __call__(self, state: DermaFlowState) -> DermaFlowState:
        start = time.time()

        logger.info(
            "Websearch started | session=%s query='%s'",
            state["session_id"],
            state["query"]
        )

        try:
            # optional vision fallback features
            vision_features = state.get("vision_features")

            # build optimized dermatology query
            search_query = build_search_query(
                query=state["query"],
                features=vision_features
            )

            logger.info(
                "Search query built | '%s' | session=%s",
                search_query,
                state["session_id"]
            )

            # ── Tavily Search ───────────────────
            tavily_response = self.tavily_client.search(
                query=search_query,
                max_results=4,
                search_depth="basic"
            )

            results = tavily_response.get("results", [])

            logger.info(
                "Tavily returned %d results | session=%s",
                len(results),
                state["session_id"]
            )

            # no results found
            if not results:
                return {
                    **state,
                    "response": (
                        "I could not find reliable dermatology "
                        "information for this query."
                    ),
                    "retrieved_chunks": [],
                    "agent_used": "websearch_agent",
                    "confident": False,
                    "error": "no_results"
                }

            # ── format retrieved results ───────
            formatted_results = format_results(results)

            # ── build LLM prompt ───────────────
            prompt = WEBSEARCH_RESPONSE_PROMPT.format(
                query=state["query"],
                results=formatted_results
            )

            # ── Gemini summarization ───────────
            llm_response = self.model.generate_content(prompt)
            answer = llm_response.text

            latency = round((time.time() - start) * 1000, 2)

            logger.info(
                "Websearch complete | latency=%sms | session=%s",
                latency,
                state["session_id"]
            )

            return {
                **state,
                "response": answer,
                "retrieved_chunks": [],
                "agent_used": "websearch_agent",
                "confident": True,
                "latency_ms": latency,
                "error": None
            }

        except Exception as e:
            logger.error(
                "Websearch failed | error=%s | session=%s",
                str(e),
                state["session_id"]
            )

            return {
                **state,
                "response": (
                    "Web search is currently unavailable. "
                    "Please try again later."
                ),
                "retrieved_chunks": [],
                "agent_used": "websearch_agent",
                "confident": False,
                "error": str(e)
            }

# Instantiate with dependencies injected
_model = genai.GenerativeModel(config.LLM_MODEL)
_tavily = TavilyClient(api_key=config.TAVILY_API_KEY)
websearch_agent = WebSearchAgent(model=_model, tavily_client=_tavily)
