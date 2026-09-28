from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles   # ✅ Added (required for PDF downloads)
from pydantic import BaseModel

from agent_manager import agent_manager
from memory.memory_engine import read_user, update_user_key, append_history_entry
from notes.notes_engine import (
    list_notes,
    create_note,
    update_note_by_id,
    delete_note_by_id,
)
from notes.notes_engine import (
    list_notes,
    create_note,
    update_note_by_id,
    delete_note_by_id,
    get_note_history,         # NEW
    restore_note_version      # NEW
)

from tasks.tasks_engine import (
    list_tasks,
    create_task,
    update_task_by_id,
    delete_task_by_id,
)

# ---------------------------------------------------------
# APP INITIALIZATION
# ---------------------------------------------------------
app = FastAPI()

# Allow frontend to fetch
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# SERVE PDF FILES (NEW)
# ---------------------------------------------------------
# This allows: http://localhost:9000/pdf/<filename>
app.mount("/pdf-files", StaticFiles(directory="pdf"), name="pdf-files")   # ✅ REQUIRED FIX


# ---------------------------------------------------------
# MODELS
# ---------------------------------------------------------
class CommandRequest(BaseModel):
    user_id: str
    command: str
    params: dict | None = None


# ---------------------------------------------------------
# BASIC ROUTES
# ---------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok", "service": "Saketh CommandOS Backend"}


# ---------------------------------------------------------
# MEMORY ROUTES
# ---------------------------------------------------------
@app.get("/memory/{user_id}")
def memory_fetch(user_id: str):
    try:
        return read_user(user_id)
    except Exception as e:
        raise HTTPException(500, f"Memory read failed: {e}")


@app.post("/memory/update")
def memory_update(req: dict):
    try:
        update_user_key(req["user_id"], req["key"], req["value"])
        return {"status": "updated"}
    except Exception as e:
        raise HTTPException(500, f"Memory update failed: {e}")


# ---------------------------------------------------------
# COMMAND ROUTE
# ---------------------------------------------------------
from core.command_router import route_command

@app.post("/command")
def run_command(req: CommandRequest):
    try:
        result = route_command(req.user_id, req.command)

        # Append to history safely
        try:
            append_history_entry(req.user_id, {
                "agent": result.get("agent", "unknown"),
                "message": result.get("response") or str(result),
            })
        except:
            pass

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent routing failed: {str(e)}")


# ---------------------------------------------------------
# PDF GENERATION
# ---------------------------------------------------------
from pdf.pdf_generator import generate_pdf

class PDFRequest(BaseModel):
    report_type: str
    summary: str
    details: str


@app.post("/pdf/create")
def create_pdf(req: PDFRequest):
    try:
        path = generate_pdf(req.report_type, req.summary, req.details)
        return {"status": "success", "path": path}
    except Exception as e:
        raise HTTPException(500, f"PDF generation failed: {e}")
    
import os

@app.get("/pdf/list")
def list_pdfs():
    try:
        files = os.listdir("pdf")  # folder where PDFs are stored
        # Filter only .pdf files
        pdf_files = [f for f in files if f.lower().endswith(".pdf")]
        # Sort newest first
        pdf_files.sort(key=lambda x: os.path.getmtime(os.path.join("pdf", x)), reverse=True)
        return {"files": pdf_files}
    except Exception as e:
        raise HTTPException(500, f"Could not list PDFs: {e}")


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)


# ---------------------------------------------------------
# NOTES ROUTES
# ---------------------------------------------------------

class NoteCreate(BaseModel):
    user_id: str
    title: str
    content: str
    tags: list[str] | None = None
    pinned: bool | None = False


class NoteUpdate(BaseModel):
    user_id: str
    title: str | None = None
    content: str | None = None
    tags: list[str] | None = None
    pinned: bool | None = None


@app.get("/notes/{user_id}")
def notes_list(user_id: str):
    try:
        notes = list_notes(user_id)
        return {"status": "ok", "notes": notes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"notes list failed: {str(e)}")


@app.post("/notes/create")
def notes_create(req: NoteCreate):
    try:
        note = create_note(req.user_id, req.title, req.content, req.tags or [], req.pinned or False)
        return {"status": "created", "note": note}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"notes create failed: {str(e)}")


@app.put("/notes/update/{note_id}")
def notes_update(note_id: int, req: NoteUpdate):
    try:
        patch = {}
        if req.title is not None:
            patch["title"] = req.title
        if req.content is not None:
            patch["content"] = req.content
        if req.tags is not None:           # NEW
            patch["tags"] = req.tags
        if req.pinned is not None:
            patch["pinned"] = req.pinned


        updated = update_note_by_id(req.user_id, note_id, patch)
        return {"status": "updated", "note": updated}
    except KeyError:
        raise HTTPException(status_code=404, detail="note not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"notes update failed: {str(e)}")


@app.delete("/notes/delete/{note_id}")
def notes_delete(note_id: int, user_id: str):
    try:
        ok = delete_note_by_id(user_id, note_id)
        if ok:
            return {"status": "deleted"}
        raise HTTPException(status_code=404, detail="note not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"notes delete failed: {str(e)}")


# ---------------------------------------------------------
# TASKS ROUTES
# ---------------------------------------------------------
class TaskCreate(BaseModel):
    user_id: str
    title: str
    description: str | None = None
    due_date: str | None = None


class TaskUpdate(BaseModel):
    user_id: str
    title: str | None = None
    description: str | None = None
    due_date: str | None = None
    status: str | None = None
    completed: bool | None = None


@app.get("/tasks/{user_id}")
def tasks_list(user_id: str):
    try:
        tasks = list_tasks(user_id)
        return {"status": "ok", "tasks": tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tasks list failed: {str(e)}")


@app.post("/tasks/create")
def tasks_create(req: TaskCreate):
    try:
        t = create_task(req.user_id, req.title, req.description or "", req.due_date)
        return {"status": "created", "task": t}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tasks create failed: {str(e)}")


@app.put("/tasks/update/{task_id}")
def tasks_update(task_id: int, req: TaskUpdate):
    try:
        patch = {}
        if req.title is not None:
            patch["title"] = req.title
        if req.description is not None:
            patch["description"] = req.description
        if req.due_date is not None:
            patch["due_date"] = req.due_date
        if req.status is not None:
            patch["status"] = req.status
        if req.completed is not None:
            patch["completed"] = req.completed

        updated = update_task_by_id(req.user_id, task_id, patch)
        return {"status": "updated", "task": updated}
    except KeyError:
        raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tasks update failed: {str(e)}")


@app.delete("/tasks/delete/{task_id}")
def tasks_delete(task_id: int, user_id: str):
    try:
        ok = delete_task_by_id(user_id, task_id)
        if ok:
            return {"status": "deleted"}
        raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tasks delete failed: {str(e)}")


# ---------------------------------------------------------
# TIMELINE ROUTE
# ---------------------------------------------------------
@app.get("/history/all")
def get_all_history():
    try:
        data = read_user("saketh")
        if isinstance(data, dict):
            history = data.get("history", [])
            if isinstance(history, list):
                return history
        return []
    except Exception as e:
        print("Failed to load timeline history:", e)
        return []

@app.get("/notes/history/{note_id}")
def notes_history(note_id: int, user_id: str):
    try:
        hist = get_note_history(user_id, note_id)
        return {"status": "ok", "history": hist}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"history failed: {e}")


@app.post("/notes/restore/{note_id}")
def notes_restore(note_id: int, payload: dict):
    try:
        user_id = payload.get("user_id")
        index = payload.get("index")
        restored = restore_note_version(user_id, note_id, index)
        return {"status": "restored", "note": restored}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"restore failed: {e}")

@app.post("/run-command")
def run_command_alias(req: CommandRequest):
    return run_command(req)
