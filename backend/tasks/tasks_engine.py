# backend/tasks/tasks_engine.py
import os
import json
from typing import List, Dict, Any
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

def _user_file(user_id: str) -> str:
    safe = "".join(c for c in user_id if c.isalnum() or c in ("-", "_")).lower()
    return os.path.join(DATA_DIR, f"{safe}.json")

def _read_user_tasks(user_id: str) -> Dict[str, Any]:
    path = _user_file(user_id)
    if not os.path.exists(path):
        return {"tasks": []}
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return {"tasks": []}

def _write_user_tasks(user_id: str, data: Dict[str, Any]):
    path = _user_file(user_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def list_tasks(user_id: str) -> List[Dict[str, Any]]:
    data = _read_user_tasks(user_id)
    return data.get("tasks", [])

def _next_id(tasks: List[Dict[str, Any]]) -> int:
    if not tasks:
        return 1
    return max((t.get("id", 0) for t in tasks), default=0) + 1

def create_task(user_id: str, title: str, description: str = "", due_date: str | None = None) -> Dict[str, Any]:
    data = _read_user_tasks(user_id)
    tasks = data.get("tasks", [])
    tid = _next_id(tasks)
    now = datetime.utcnow().isoformat() + "Z"
    task = {
        "id": tid,
        "title": title or "",
        "description": description or "",
        "due_date": due_date,
        "status": "todo",
        "created_at": now,
        "completed": False,
    }
    tasks.append(task)
    data["tasks"] = tasks
    _write_user_tasks(user_id, data)
    return task

def update_task_by_id(user_id: str, task_id: int, patch: Dict[str, Any]) -> Dict[str, Any]:
    data = _read_user_tasks(user_id)
    tasks = data.get("tasks", [])
    updated = None
    for i, t in enumerate(tasks):
        try:
            if int(t.get("id")) == int(task_id):
                tasks[i] = {**t, **patch}
                updated = tasks[i]
                break
        except Exception:
            continue
    if updated is None:
        raise KeyError("task not found")
    data["tasks"] = tasks
    _write_user_tasks(user_id, data)
    return updated

def delete_task_by_id(user_id: str, task_id: int) -> bool:
    data = _read_user_tasks(user_id)
    tasks = data.get("tasks", [])
    new_tasks = [t for t in tasks if int(t.get("id")) != int(task_id)]
    if len(new_tasks) == len(tasks):
        return False
    data["tasks"] = new_tasks
    data["tasks"] = new_tasks
    _write_user_tasks(user_id, data)
    return True
