import logging
from langgraph.graph import END, StateGraph

from agents.rag_agent import rag_agent
from agents.state import DermaFlowState
from agents.triage_agent import triage_agent
from agents.vision_agent import vision_agent
from agents.websearch_agent import websearch_agent

logger = logging.getLogger("orchestrator")


def route_from_triage(state: DermaFlowState) -> str:
    intent = state.get("intent", "condition_info")

    logger.info(
        "Routing query | intent=%s | session=%s",
        intent,
        state["session_id"]
    )

    if intent in {"condition_info", "ingredient"}:
        return "rag_agent"

    if intent == "web_search":
        return "websearch_agent"

    if intent == "image":
        return "vision_agent"

    # fallback safety
    return "rag_agent"


def route_from_rag(state: DermaFlowState) -> str:
    if state.get("confident", False):
        return "end"
    return "websearch_agent"


workflow = StateGraph(DermaFlowState)

# nodes
workflow.add_node("triage_agent", triage_agent)
workflow.add_node("rag_agent", rag_agent)
workflow.add_node("websearch_agent", websearch_agent)
workflow.add_node("vision_agent", vision_agent)

# entry point
workflow.set_entry_point("triage_agent")

# routing
workflow.add_conditional_edges(
    "triage_agent",
    route_from_triage,
    {
        "rag_agent": "rag_agent",
        "websearch_agent": "websearch_agent",
        "vision_agent": "vision_agent",
    },
)

# endings
workflow.add_conditional_edges(
    "rag_agent",
    route_from_rag,
    {
        "end": END,
        "websearch_agent": "websearch_agent"
    }
)
workflow.add_edge("websearch_agent", END)
workflow.add_edge("vision_agent", END)

# compile
app = workflow.compile()

logger.info("DermaFlow graph compiled successfully")