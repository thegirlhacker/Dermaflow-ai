from typing import List, TypedDict, Optional
#So state contains: all important variables that may be needed between nodes
class DermaFlowState(TypedDict):

    # ── user input ─────────────────────
    query: str
    condition: Optional[str]
    image_path: Optional[str]
    session_id: str

    # ── routing ────────────────────────
    intent: Optional[str]

    # ── agent outputs ──────────────────
    retrieved_chunks: List[str]
    response: str

    # ── metadata ───────────────────────
    agent_used: str
    error: Optional[str]