from typing import TypedDict, Optional, List, Dict, Any

class DermaFlowState(TypedDict):
    query: str
    condition: Optional[str]
    image_path: Optional[str]
    session_id: str
    history: List[Dict[str, str]]
    intent: Optional[str]
    retrieved_chunks: List[Dict[str, Any]]
    response: str
    agent_used: str
    confident: bool
    latency_ms: float
    vision_features: Optional[Dict[str, Any]]
    vision_condition_scores: Optional[Dict[str, float]]
    error: Optional[str]
