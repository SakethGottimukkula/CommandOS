import os
import json
from datetime import datetime
from typing import List, Dict, Any

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def _user_file(user_id: str) -> str:
    safe = "".join(c for c in user_id if c.isalnum() or c in ("-", "_")).lower()
    return os.path.join(DATA_DIR, f"{safe}.json")

def _read_user_notes(user_id: str) -> Dict[str, Any]:
    path = _user_file(user_id)
    if not os.path.exists(path):
        return {"notes": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _write_user_notes(user_id: str, data: Dict[str, Any]):
    path = _user_file(user_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _next_id(notes: List[Dict[str, Any]]) -> int:
    if not notes:
        return 1
    return max((n.get("id", 0) for n in notes), default=0) + 1


# --------------------------------------------------------------------------------
#   CREATE NOTE
# --------------------------------------------------------------------------------
def create_note(user_id: str, title: str, content: str, tags=None, pinned=False):
    data = _read_user_notes(user_id)
    notes = data.get("notes", [])

    nid = _next_id(notes)
    note = {
        "id": nid,
        "title": title or "",
        "content": content or "",
        "tags": tags or [],
        "pinned": pinned,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "history": []         # <-- NEW
    }

    notes.append(note)
    data["notes"] = notes
    _write_user_notes(user_id, data)
    return note


# --------------------------------------------------------------------------------
#   UPDATE NOTE + SAVE TO HISTORY
# --------------------------------------------------------------------------------
def update_note_by_id(user_id: str, note_id: int, patch: Dict[str, Any]):
    data = _read_user_notes(user_id)
    notes = data.get("notes", [])
    updated = None

    for i, n in enumerate(notes):
        if int(n.get("id")) == int(note_id):

            # Ensure fields exist for old notes
            if "tags" not in n:
                n["tags"] = []
            if "pinned" not in n:
                n["pinned"] = False
            if "history" not in n:
                n["history"] = []

            # Save the current state to history BEFORE updating
            history_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "title": n.get("title"),
                "content": n.get("content"),
                "tags": n.get("tags", []),
                "pinned": n.get("pinned", False)
            }
            n["history"].append(history_entry)

            # Keep only last 20 versions
            n["history"] = n["history"][-20:]

            # Apply patch
            notes[i] = {
                **n,
                **patch,
                "updated_at": datetime.utcnow().isoformat()
            }
            updated = notes[i]
            break

    if updated is None:
        raise KeyError("note not found")

    data["notes"] = notes
    _write_user_notes(user_id, data)
    return updated


# --------------------------------------------------------------------------------
#   DELETE NOTE
# --------------------------------------------------------------------------------
def delete_note_by_id(user_id: str, note_id: int) -> bool:
    data = _read_user_notes(user_id)
    notes = data.get("notes", [])
    new_notes = [n for n in notes if int(n.get("id")) != int(note_id)]
    if len(new_notes) == len(notes):
        return False
    data["notes"] = new_notes
    _write_user_notes(user_id, data)
    return True


# --------------------------------------------------------------------------------
#   LIST NOTES (SORTING)
# --------------------------------------------------------------------------------
def list_notes(user_id: str):
    data = _read_user_notes(user_id)
    notes = data.get("notes", [])

    # Ensure compatibility
    for n in notes:
        if "tags" not in n:
            n["tags"] = []
        if "pinned" not in n:
            n["pinned"] = False
        if "history" not in n:
            n["history"] = []

    # Sort: pinned FIRST, latest updated FIRST
    def sort_key(n):
        return (
            0 if n.get("pinned") else 1,
            n.get("updated_at", ""),
            n.get("id", 0),
        )

    return sorted(notes, key=sort_key, reverse=True)


# --------------------------------------------------------------------------------
#   GET HISTORY (NEW)
# --------------------------------------------------------------------------------
def get_note_history(user_id: str, note_id: int):
    data = _read_user_notes(user_id)
    notes = data.get("notes", [])
    for n in notes:
        if int(n.get("id")) == int(note_id):
            return n.get("history", [])
    return []


# --------------------------------------------------------------------------------
#   RESTORE NOTE FROM HISTORY (NEW)
# --------------------------------------------------------------------------------
def restore_note_version(user_id: str, note_id: int, index: int):
    data = _read_user_notes(user_id)
    notes = data.get("notes", [])

    for i, n in enumerate(notes):
        if int(n.get("id")) == int(note_id):
            history = n.get("history", [])
            if index < 0 or index >= len(history):
                raise KeyError("invalid history index")

            version = history[index]

            # overwrite fields
            n["title"] = version["title"]
            n["content"] = version["content"]
            n["tags"] = version["tags"]
            n["pinned"] = version["pinned"]
            n["updated_at"] = datetime.utcnow().isoformat()

            notes[i] = n
            break

    data["notes"] = notes
    _write_user_notes(user_id, data)
    return notes[i]
