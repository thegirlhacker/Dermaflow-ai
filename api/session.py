from pymongo import MongoClient
from config import config

# single connection at module level
_client = MongoClient(config.MONGO_URI)
_col    = _client["dermaflow"]["sessions"]


# ─────────────────────────────────────────────
# create new session
# ─────────────────────────────────────────────

def create_session(session_id: str):
    # only insert if it doesn't already exist
    # prevents duplicates if called twice
    if not _col.find_one({"session_id": session_id}):
        _col.insert_one({
            "session_id": session_id,
            "history":    []
        })


# ─────────────────────────────────────────────
# get session
# ─────────────────────────────────────────────

def get_session(session_id: str) -> dict:
    session = _col.find_one(
        {"session_id": session_id},
        {"_id": 0}          # exclude ObjectId — not JSON serializable
    )

    if not session:
        create_session(session_id)
        return {"session_id": session_id, "history": []}

    return session


# ─────────────────────────────────────────────
# save session
# ─────────────────────────────────────────────

def save_session(session_id: str, data: dict):
    _col.update_one(
        {"session_id": session_id},
        {"$set": data},
        upsert=True     # creates doc if missing — safety net
    )