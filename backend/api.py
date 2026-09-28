# backend/api.py
from fastapi import FastAPI
from pydantic import BaseModel
from core.command_router import route_command
import uvicorn

app = FastAPI()

class CommandRequest(BaseModel):
    user_id: str
    command: str

@app.get("/")
def home():
    return {"status": "MAS API running"}

@app.post("/run-command")
def execute_command(data: CommandRequest):
    try:
        result = route_command(data.user_id, data.command)
        return result
    except Exception as e:
        return {"response": f"Router error: {str(e)}", "action": "error"}

# alias: provide /command as well so frontend is safe either way
@app.post("/command")
def execute_command_alias(data: CommandRequest):
    return execute_command(data)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
