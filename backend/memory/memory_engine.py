import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "memory.json")


# Ensure database file exists
if not os.path.exists(DB_PATH):
    with open(DB_PATH, "w") as f:
        json.dump({"users": {}, "history": {}}, f)


def read_db():
    with open(DB_PATH, "r") as f:
        return json.load(f)


def write_db(data):
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=4)


def read_user(user_id):
    db = read_db()
    return db["users"].get(user_id, {"tasks": [], "history": []})


def update_user_key(user_id, key, value):
    db = read_db()
    if user_id not in db["users"]:
        db["users"][user_id] = {}

    db["users"][user_id][key] = value
    write_db(db)


def append_history_entry(user_id, entry):
    """
    entry = {
      "agent": "study",
      "message": "...",
      "timestamp": "2025-01-01T10:00:00Z"
    }
    """
    db = read_db()

    if user_id not in db["users"]:
        db["users"][user_id] = {"history": []}

    if "history" not in db["users"][user_id]:
        db["users"][user_id]["history"] = []

    entry["timestamp"] = datetime.utcnow().isoformat() + "Z"

    db["users"][user_id]["history"].append(entry)
    write_db(db)
