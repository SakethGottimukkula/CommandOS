# agents/task_agent.py
from core.nlp_parser import NLPParser, Parsed
from tasks.tasks_engine import (
    list_tasks,
    create_task,
    update_task_by_id,
    delete_task_by_id,
)
from typing import Dict, Any

def _find_task_by_query(tasks, query):
    """
    Return the best matching task dict or None.
    Matching strategy:
      1) exact id if query is numeric
      2) exact title match (case-insensitive)
      3) substring match (title contains query)
      4) fuzzy beginswith
    """
    q = (query or "").strip().lower()
    if not q:
        return None

    # numeric id match
    if q.isdigit():
        tid = int(q)
        for t in tasks:
            if int(t.get("id", -1)) == tid:
                return t

    # exact title
    for t in tasks:
        if (t.get("title") or "").strip().lower() == q:
            return t

    # substring match
    for t in tasks:
        if q in (t.get("title") or "").lower():
            return t

    # startswith
    for t in tasks:
        if (t.get("title") or "").lower().startswith(q):
            return t

    return None

class TaskAgent:
    def handle(self, raw_command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Accepts raw text command and returns an agent response dict.

        Uses the NLPParser to detect intent and then uses tasks_engine for persistence.
        """
        params = params or {}
        parsed = NLPParser.parse(raw_command)

        try:
            if parsed.intent == "add_task":
                title = parsed.slots.get("title") or raw_command
                # create using tasks_engine
                t = create_task("saketh", title, parsed.slots.get("description", "") or "")
                return {"agent": "task", "action": "add_task", "status": "ok", "task": t, "response": f'Task added: "{t["title"]}"'}

            if parsed.intent == "list_tasks":
                tasks = list_tasks("saketh")
                if not tasks:
                    return {"agent": "task", "action": "list_tasks", "status": "ok", "response": "No tasks yet."}
                # Build readable text
                lines = []
                for t in tasks:
                    mark = "✔" if t.get("completed") else "✗"
                    lines.append(f'{t.get("id")}) {t.get("title")} [{mark}]')
                return {"agent": "task", "action": "list_tasks", "status": "ok", "tasks": tasks, "response": "\n".join(lines)}

            if parsed.intent == "complete_task":
                query = parsed.slots.get("query") or ""
                tasks = list_tasks("saketh")
                found = _find_task_by_query(tasks, query)
                if not found:
                    return {"agent": "task", "action": "complete_task", "status": "error", "response": f'No task matched "{query}"'}
                updated = update_task_by_id("saketh", int(found["id"]), {"completed": True, "status": "done"})
                return {"agent": "task", "action": "complete_task", "status": "ok", "task": updated, "response": f'Completed: "{updated.get("title")}"'}

            if parsed.intent == "delete_task":
                query = parsed.slots.get("query") or ""
                tasks = list_tasks("saketh")
                found = _find_task_by_query(tasks, query)
                if not found:
                    return {"agent": "task", "action": "delete_task", "status": "error", "response": f'No task matched "{query}"'}
                ok = delete_task_by_id("saketh", int(found["id"]))
                if ok:
                    return {"agent": "task", "action": "delete_task", "status": "ok", "response": f'Deleted: "{found.get("title")}"'}
                else:
                    return {"agent": "task", "action": "delete_task", "status": "error", "response": "Failed to delete task."}

            # fallback
            return {"agent": "task", "status": "error", "response": "Could not understand task command."}
        except KeyError:
            return {"agent": "task", "status": "error", "response": "Task not found."}
        except Exception as e:
            return {"agent": "task", "status": "error", "response": f"Internal error: {str(e)}"}
