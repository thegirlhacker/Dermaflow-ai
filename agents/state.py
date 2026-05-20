from typing import Any, Optional, TypedDict

#So state contains: all important variables that may be needed between nodes
class DermaFlowState(TypedDict):

    # ── user input ─────────────────────
    query: str
    condition: Optional[str]
    image_path: Optional[str]
    session_id: str

    # ── conversation history ───────────
    history: list[dict[str, Any]]

    # ── routing ────────────────────────
    intent: Optional[str]

    # ── agent outputs ──────────────────
    retrieved_chunks: list[dict[str, Any]]
    response: str

    # ── metadata ───────────────────────
    agent_used: str
    confident: bool
    error: Optional[str]