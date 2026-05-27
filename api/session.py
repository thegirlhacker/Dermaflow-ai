

from pymongo import MongoClient
import datetime
from config import config

# single connection at module level
_client = MongoClient(config.MONGO_URI)
_col    = _client["dermaflow"]["sessions"]

def create_session(session_id: str, title: str = "New Chat"):
    if not _col.find_one({"session_id": session_id}):
        now = datetime.datetime.utcnow()
        _col.insert_one({
            "session_id": session_id,
            "title": title,
            "history": [],
            "created_at": now,
            "updated_at": now
        })

def get_session(session_id: str) -> dict:
    session = _col.find_one(
        {"session_id": session_id},
        {"_id": 0}
    )
    if not session:
        create_session(session_id)
        return get_session(session_id)
    return session

def save_session(session_id: str, data: dict):
    data["updated_at"] = datetime.datetime.utcnow()
    _col.update_one(
        {"session_id": session_id},
        {"$set": data},
        upsert=True
    )

def list_sessions() -> list:
    sessions = _col.find(
        {"history.0": {"$exists": True}},
        {"_id": 0, "session_id": 1, "title": 1, "updated_at": 1}
    ).sort("updated_at", -1)
    
    # Ensure backward compatibility for older sessions without a title
    result = []
    for s in sessions:
        if "title" not in s:
            s["title"] = "Previous Chat"
        result.append(s)
        
    return result
