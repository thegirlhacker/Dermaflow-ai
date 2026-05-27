from pydantic import BaseModel, Field 
from typing import Optional


# ── Request models ────────────────────────────────────────
# request from frontend
class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = Field(None, description="Pass existing session_id to continue conversation")
    condition_hint: Optional[str] = Field(None, description="Optional condition hint from frontend")
    image_base64: Optional[str] = Field(None, description="Optional base64 encoded image for vision agent")

#class ImageAnalysisRequest(BaseModel):
    #session_id: Optional[str] = None
    #additional_context: Optional[str] = Field(None, description="Any extra info user wants to add alongside image")

# ── Response models ───────────────────────────────────────

class SourceChunk(BaseModel):
    source: str
    condition: str
    score: float
    preview: str 
             # first 100 chars of the chunk text
# retrieved source preview
class ChatResponse(BaseModel):
    session_id: str
    response: str
    agent_used: str       # which agent handled it: rag, websearch, vision, triage
    sources: list[SourceChunk]
    confident: bool
    latency_ms: float

#class ImageAnalysisResponse(BaseModel):
    #session_id: str
    #visual_description: str   # what the vision model saw
    #rag_response: str         # what RAG returned based on description
    #agent_used: str
    #sources: list[SourceChunk]
    #confident: bool

