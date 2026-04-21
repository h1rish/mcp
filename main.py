from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI()

# =========================
# 🧠 MEMORY LAYER
# =========================

memory_store: Dict[str, Dict[str, Any]] = {}

def save_memory(user_id: str, key: str, value: Any):
    if user_id not in memory_store:
        memory_store[user_id] = {}
    memory_store[user_id][key] = value

def get_memory(user_id: str):
    return memory_store.get(user_id, {})


# =========================
# 🧰 TOOL INPUT MODELS
# =========================

class StudentRequest(BaseModel):
    user_id: str
    student_id: str


class MemoryRequest(BaseModel):
    user_id: str
    key: str
    value: Any


# =========================
# 🟢 TOOLS (AI FOUNDARY READY)
# =========================

@app.post("/tools/get_student")
def get_student(req: StudentRequest):

    student_data = {
        "id": req.student_id,
        "name": "John Doe",
        "course": "AI & ML",
        "marks": 85
    }

    save_memory(req.user_id, "last_student", student_data)

    return {
        "tool": "get_student",
        "data": student_data
    }


@app.post("/tools/save_memory")
def save_memory_tool(req: MemoryRequest):

    save_memory(req.user_id, req.key, req.value)

    return {
        "tool": "save_memory",
        "status": "saved"
    }


@app.get("/tools/get_memory/{user_id}")
def get_memory_tool(user_id: str):

    return {
        "tool": "get_memory",
        "memory": get_memory(user_id)
    }


@app.get("/tools/ping")
def ping():
    return {"tool": "ping", "status": "ok"}


# =========================
# BASIC ENDPOINTS
# =========================

@app.get("/")
def home():
    return {"message": "MCP Server Running (Stage 2)"}


@app.get("/health")
def health():
    return {"status": "ok"}
