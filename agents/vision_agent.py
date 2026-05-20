from agents.state import DermaFlowState


def vision_agent(state: DermaFlowState) -> DermaFlowState:
    return {
        **state,
        "agent_used": "vision_agent",
        "response": "Vision analysis support is not implemented yet.",
    }
