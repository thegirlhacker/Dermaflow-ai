import sys
import os
sys.path.append("/home/aarushi/Dermaflow-ai")
from pymongo import MongoClient
from config import config

client = MongoClient(config.MONGO_URI)
col = client["dermaflow"]["sessions"]

# Let's see what we have
all_sessions = list(col.find({}, {"title": 1, "history": 1}))
print(f"Total sessions: {len(all_sessions)}")
empty = [s for s in all_sessions if not s.get("history")]
print(f"Empty sessions: {len(empty)}")

# Delete empty sessions to clean up the DB
res = col.delete_many({"$or": [{"history": {"$size": 0}}, {"history": {"$exists": False}}]})
print(f"Deleted {res.deleted_count} empty sessions")
