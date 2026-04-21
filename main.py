from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI()

# =========================
# SIMPLE AUTH (ONLY THIS)
# =========================
API_KEY = "1234"

def verify_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


# =========================
# MEMORY
# =========================
memory_store: Dict[str, Dict[str, Any]] = {}

def save_memory(user_id: str, key: str, value: Any):
    if user_id not in memory_store:
        memory_store[user_id] = {}
    memory_store[user_id][key] = value

def get_memory(user_id: str):
    return memory_store.get(user_id, {})


# =========================
# MODELS
# =========================
class StudentRequest(BaseModel):
    user_id: str
    student_id: str


class MemoryRequest(BaseModel):
    user_id: str
    key: str
    value: Any


# =========================
# TOOLS
# =========================

@app.post("/tools/get_student")
def get_student(req: StudentRequest, x_api_key: str = Header(None)):
    verify_key(x_api_key)

    return {
        "tool": "get_student",
        "data": {
            "id": req.student_id,
            "name": "John Doe",
            "course": "AI & ML",
            "marks": 85
        }
    }


@app.post("/tools/save_memory")
def save_memory_tool(req: MemoryRequest, x_api_key: str = Header(None)):
    verify_key(x_api_key)

    save_memory(req.user_id, req.key, req.value)

    return {
        "tool": "save_memory",
        "status": "saved"
    }


@app.get("/tools/get_memory/{user_id}")
def get_memory_tool(user_id: str, x_api_key: str = Header(None)):
    verify_key(x_api_key)

    return {
        "tool": "get_memory",
        "memory": get_memory(user_id)
    }


@app.get("/tools/ping")
def ping(x_api_key: str = Header(None)):
    verify_key(x_api_key)
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
