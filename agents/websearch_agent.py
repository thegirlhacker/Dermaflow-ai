from agents.state import DermaFlowState


def websearch_agent(state: DermaFlowState) -> DermaFlowState:
    return {
        **state,
        "agent_used": "websearch_agent",
        "response": "Web search support is not implemented yet.",
    }
