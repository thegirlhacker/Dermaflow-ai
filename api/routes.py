import base64
import os
import time
import uuid

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

from agents.orchestrator import app
from api.session import create_session, get_session, save_session, list_sessions
from agents.state import DermaFlowState
from config import config
import google.generativeai as genai

router = APIRouter(prefix="/api/v1")

class SourceChunk(BaseModel):
    source: str
    condition: str
    score: float
    preview: str

class ChatResponse(BaseModel):
    session_id: str
    response: str
    agent_used: str
    sources: List[SourceChunk]
    confident: bool
    latency_ms: float

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    query: str
    condition_hint: Optional[str] = None
    image_base64: Optional[str] = None

@router.post("/new-chat")
async def new_chat():
    session_id = str(uuid.uuid4())
    create_session(session_id)
    return {"session_id": session_id}

@router.get("/sessions")
async def get_all_sessions():
    sessions = list_sessions()
    return {"sessions": sessions}

@router.get("/sessions/{session_id}")
async def get_session_history(session_id: str):
    session = get_session(session_id)
    return {"session": session}

def generate_chat_title(query: str) -> str:
    try:
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel(config.LLM_MODEL)
        prompt = f"Generate a very short, 2-3 word title for a chat session starting with this query: '{query}'. Reply ONLY with the title."
        for _ in range(3):
            try:
                response = model.generate_content(prompt)
                return response.text.strip().replace('"', '')
            except Exception:
                time.sleep(2)
        return "New Chat" # Fallback if all 3 attempts fail
    except Exception as e:
        print(f"Error generating title: {e}")
        return "New Chat"

import asyncio

def _background_generate_title(session_id: str, query: str, history: list):
    title = generate_chat_title(query)
    save_session(session_id, {"title": title, "history": history})

# ─────────────────────────────────────────────
# main chat endpoint
# ─────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    start_time = time.time()

    session_id = request.session_id or str(uuid.uuid4())
    create_session(session_id)

    image_path = None
    if request.image_base64:
        try:
            # handle 'data:image/jpeg;base64,...' prefix if present
            base64_data = request.image_base64
            if "," in base64_data:
                base64_data = base64_data.split(",")[1]
            image_bytes = base64.b64decode(base64_data)
            
            # create sample_images dir if it doesn't exist
            os.makedirs("sample_images", exist_ok=True)
            image_filename = f"sample_images/upload_{uuid.uuid4().hex[:8]}.jpg"
            with open(image_filename, "wb") as f:
                f.write(image_bytes)
            image_path = image_filename
        except Exception as e:
            print(f"Error decoding base64 image: {e}")

    session = get_session(session_id)
    history = session.get("history", [])

    if len(history) == 0:
        # User requested comment: We put title generation in the background so it doesn't block the main thread and helps prevent rate-limit bursts.
        # This was implemented in api/routes.py
        asyncio.create_task(asyncio.to_thread(_background_generate_title, session_id, request.query, history))

    initial_state: DermaFlowState = {

        "query": request.query,
        "condition": request.condition_hint,
        "image_path": image_path,
        "session_id": session_id,
        "history": history,
        "intent": None,
        "retrieved_chunks": [],
        "response": "",
        "agent_used": "",
        "confident": False,
        "error": None
    }

    output = app.invoke(initial_state)
    answer = output.get("response", "")

    # Re-fetch session to get latest history in case of parallel updates (though unlikely here)
    session = get_session(session_id)
    history = session.get("history", [])
    history.append({"role": "user",      "content": request.query})
    history.append({"role": "assistant", "content": answer})

    save_session(session_id, {"history": history})

    latency_ms = round((time.time() - start_time) * 1000, 2)

    sources = [
        SourceChunk(
            source    = c.get("source",    "unknown"),
            condition = c.get("condition", "unknown"),
            score     = c.get("score",     0.0),
            preview   = c.get("text",      "")[:120]
        )
        for c in output.get("retrieved_chunks", [])
    ]

    return ChatResponse(
        session_id = session_id,
        response   = answer,
        agent_used = output.get("agent_used", ""),
        sources    = sources,
        confident  = output.get("confident", False),
        latency_ms = latency_ms
    )


# ─────────────────────────────────────────────
# health check
# ─────────────────────────────────────────────

@router.get("/health")
async def health():
    try:
        from rag.vectordb import index
        stats = index.describe_index_stats()
        return {
            "status":       "ok",
            "vectors":      stats.total_vector_count,
            "model":        config.LLM_MODEL
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}

