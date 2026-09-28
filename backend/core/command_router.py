# backend/core/command_router.py
from core.nlp_parser import NLPParser
from tasks.tasks_engine import create_task, list_tasks, update_task_by_id, delete_task_by_id
from memory.memory_engine import read_user, update_user_key, append_history_entry
from pdf.pdf_generator import generate_pdf
from agent_manager import agent_manager

def route_command(user_id: str, text: str):
    parsed = NLPParser.parse(text)

    # ADD
    if parsed.intent == "add_task":
        title = parsed.slots.get("title", "").strip()
        t = create_task(user_id, title, "", None)
        try:
            append_history_entry(user_id, {"agent": "tasks", "message": f"Task created: {title}"})
        except Exception:
            pass
        return {"response": f"✔ Task added: {title}", "action": "add_task", "task": t}

    # COMPLETE
    if parsed.intent == "complete_task":
        q = parsed.slots.get("query", "").strip()
        tasks = list_tasks(user_id)
        matches = [t for t in tasks if q.lower() in (t.get("title","") or "").lower()]
        if not matches:
            return {"response": f"❌ No task found: {q}", "action": "complete_task", "status": "error"}
        task = matches[0]
        updated = update_task_by_id(user_id, task["id"], {"completed": True, "status": "done"})
        try:
            append_history_entry(user_id, {"agent": "tasks", "message": f"Task completed: {task['title']}"})
        except Exception:
            pass
        return {"response": f"✔ Task completed: {task['title']}", "action": "complete_task", "task": updated}

    # DELETE
    if parsed.intent == "delete_task":
        q = parsed.slots.get("query", "").strip()
        tasks = list_tasks(user_id)
        matches = [t for t in tasks if q.lower() in (t.get("title","") or "").lower()]
        if not matches:
            return {"response": f"❌ No matching task to delete: {q}", "action": "delete_task", "status": "error"}
        task = matches[0]
        ok = delete_task_by_id(user_id, task["id"])
        try:
            append_history_entry(user_id, {"agent": "tasks", "message": f"Task deleted: {task['title']}"})
        except Exception:
            pass
        return {"response": f"✔ Task deleted: {task['title']}", "action": "delete_task", "status": "ok"}

    # LIST
    if parsed.intent == "list_tasks":
        tasks = list_tasks(user_id)
        lines = []
        for t in tasks:
            mark = "✔" if t.get("completed") else "✗"
            lines.append(f"{t.get('id')}) {t.get('title')} [{mark}]")
        return {"response": "\n".join(lines), "action": "list_tasks", "tasks": tasks}

    # MEMORY
    if parsed.intent == "memory_fetch":
        try:
            mem = read_user(user_id)
            return {"response": str(mem), "action": "memory_fetch", "memory": mem}
        except Exception:
            return {"response": "Memory fetch failed", "action": "memory_fetch", "status": "error"}

    # PDF
    if parsed.intent == "generate_pdf":
        try:
            path = generate_pdf("report", "Summary", text)
            try:
                append_history_entry(user_id, {"agent": "pdf", "message": "PDF generated"})
            except Exception:
                pass
            return {"response": f"✔ PDF generated at: {path}", "action": "generate_pdf", "path": path}
        except Exception as e:
            return {"response": f"PDF failed: {e}", "action": "generate_pdf", "status": "error"}

    # SEARCH
    if parsed.intent == "search":
        return agent_manager.route(user_id, text, {})

    # FALLBACK
    return agent_manager.route(user_id, text, {})
