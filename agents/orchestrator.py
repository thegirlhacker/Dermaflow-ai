from langgraph.graph import END, StateGraph

from agents.rag_agent import rag_agent
from agents.state import DermaFlowState
from agents.triage_agent import triage_agent
from agents.vision_agent import vision_agent
from agents.websearch_agent import websearch_agent


def route_from_triage(state: DermaFlowState) -> str:
    intent = state.get("intent")

    if intent in {"condition_info", "ingredient"}:
        return "rag_agent"
    if intent == "web_search":
        return "websearch_agent"
    if intent == "image":
        return "vision_agent"

    return "rag_agent"


workflow = StateGraph(DermaFlowState)

workflow.add_node("triage_agent", triage_agent)
workflow.add_node("rag_agent", rag_agent)
workflow.add_node("websearch_agent", websearch_agent)
workflow.add_node("vision_agent", vision_agent)

workflow.set_entry_point("triage_agent")
workflow.add_conditional_edges(
    "triage_agent",
    route_from_triage,
    {
        "rag_agent": "rag_agent",
        "websearch_agent": "websearch_agent",
        "vision_agent": "vision_agent",
    },
)
workflow.add_edge("rag_agent", END)
workflow.add_edge("websearch_agent", END)
workflow.add_edge("vision_agent", END)

app = workflow.compile()
