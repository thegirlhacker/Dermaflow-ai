import os
import json
import datetime
from pymongo import MongoClient
from config import config

# Check if MONGO_URI has placeholder or is missing
use_fallback = False
_col = None

if not config.MONGO_URI or "<db_password>" in config.MONGO_URI:
    print("Using local file-based database fallback (MONGO_URI is missing or contains placeholder).")
    use_fallback = True
else:
    try:
        # Check connection quickly with a short serverSelectionTimeoutMS
        _client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=2000)
        # Attempt to access collections
        _col = _client["dermaflow"]["sessions"]
        # Trigger a connection attempt
        _client.admin.command('ping')
        print("Connected to MongoDB successfully.")
    except Exception as e:
        print(f"MongoDB connection failed: {e}. Falling back to local file-based database.")
        use_fallback = True

# Ensure the local sessions directory exists
os.makedirs(config.SESSIONS_DIR, exist_ok=True)

def _get_local_file_path(session_id: str) -> str:
    # sanitize session_id just in case
    safe_id = "".join(c for c in session_id if c.isalnum() or c in "-_")
    return os.path.join(config.SESSIONS_DIR, f"{safe_id}.json")

def create_session(session_id: str, title: str = "New Chat"):
    global use_fallback
    if not use_fallback and _col is not None:
        try:
            if not _col.find_one({"session_id": session_id}):
                now = datetime.datetime.utcnow()
                _col.insert_one({
                    "session_id": session_id,
                    "title": title,
                    "history": [],
                    "created_at": now,
                    "updated_at": now
                })
            return
        except Exception as e:
            print(f"MongoDB create_session error: {e}. Switching to local fallback.")
            use_fallback = True

    # Local fallback
    path = _get_local_file_path(session_id)
    if not os.path.exists(path):
        now = datetime.datetime.utcnow().isoformat()
        session_data = {
            "session_id": session_id,
            "title": title,
            "history": [],
            "created_at": now,
            "updated_at": now
        }
        with open(path, "w") as f:
            json.dump(session_data, f, indent=2)

def get_session(session_id: str) -> dict:
    global use_fallback
    if not use_fallback and _col is not None:
        try:
            session = _col.find_one(
                {"session_id": session_id},
                {"_id": 0}
            )
            if not session:
                create_session(session_id)
                return get_session(session_id)
            return session
        except Exception as e:
            print(f"MongoDB get_session error: {e}. Switching to local fallback.")
            use_fallback = True

    # Local fallback
    path = _get_local_file_path(session_id)
    if not os.path.exists(path):
        create_session(session_id)
    with open(path, "r") as f:
        data = json.load(f)
    return data

def save_session(session_id: str, data: dict):
    global use_fallback
    if not use_fallback and _col is not None:
        try:
            # Convert datetime to utc if needed
            now = datetime.datetime.utcnow()
            update_data = {**data}
            if "updated_at" not in update_data:
                update_data["updated_at"] = now
            _col.update_one(
                {"session_id": session_id},
                {"$set": update_data},
                upsert=True
            )
            return
        except Exception as e:
            print(f"MongoDB save_session error: {e}. Switching to local fallback.")
            use_fallback = True

    # Local fallback
    path = _get_local_file_path(session_id)
    session_data = {}
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                session_data = json.load(f)
        except Exception:
            session_data = {}
    
    # Merge/update data
    for k, v in data.items():
        if isinstance(v, datetime.datetime):
            session_data[k] = v.isoformat()
        else:
            session_data[k] = v
            
    session_data["updated_at"] = datetime.datetime.utcnow().isoformat()
    session_data["session_id"] = session_id
    if "title" not in session_data:
        session_data["title"] = "New Chat"
    if "history" not in session_data:
        session_data["history"] = []

    with open(path, "w") as f:
        json.dump(session_data, f, indent=2)

def list_sessions() -> list:
    global use_fallback
    if not use_fallback and _col is not None:
        try:
            sessions = _col.find(
                {"history.0": {"$exists": True}},
                {"_id": 0, "session_id": 1, "title": 1, "updated_at": 1, "history": {"$slice": 1}}
            ).sort("updated_at", -1)
            
            result = []
            for s in sessions:
                if "title" not in s:
                    s["title"] = "Previous Chat"
                    
                preview = ""
                if "history" in s and len(s["history"]) > 0:
                    preview = s["history"][0].get("content", "")
                    if len(preview) > 40:
                        preview = preview[:40] + "..."
                s["preview"] = preview
                s.pop("history", None)
                result.append(s)
            return result
        except Exception as e:
            print(f"MongoDB list_sessions error: {e}. Switching to local fallback.")
            use_fallback = True

    # Local fallback
    result = []
    if not os.path.exists(config.SESSIONS_DIR):
        return []
    
    for fname in os.listdir(config.SESSIONS_DIR):
        if fname.endswith(".json"):
            try:
                with open(os.path.join(config.SESSIONS_DIR, fname), "r") as f:
                    s = json.load(f)
                
                # We only show sessions with history (same as {"history.0": {"$exists": True}})
                if not s.get("history"):
                    continue
                
                preview = ""
                if len(s["history"]) > 0:
                    preview = s["history"][0].get("content", "")
                    if len(preview) > 40:
                        preview = preview[:40] + "..."
                
                # Format to return
                result.append({
                    "session_id": s.get("session_id"),
                    "title": s.get("title", "Previous Chat"),
                    "updated_at": s.get("updated_at"),
                    "preview": preview
                })
            except Exception as e:
                print(f"Error reading session file {fname}: {e}")
                
    # Sort by updated_at descending
    result.sort(key=lambda x: x.get("updated_at", "") if x.get("updated_at") else "", reverse=True)
    return result
