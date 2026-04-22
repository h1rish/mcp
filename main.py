from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI()

# =========================
# AUTH
# =========================
API_KEY = "1234"

def verify_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


# =========================
# MEMORY STORE
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
# CORE LOGIC
# =========================
def get_student_logic(student_id: str):
    return {
        "id": student_id,
        "name": "John Doe",
        "course": "AI & ML",
        "marks": 85
    }


# =========================
# FASTAPI REST ENDPOINTS
# =========================

@app.post("/tools/get_student")
def get_student(req: StudentRequest, x_api_key: str = Header(None)):
    verify_key(x_api_key)
    return {
        "tool": "get_student",
        "data": get_student_logic(req.student_id)
    }


@app.post("/tools/save_memory")
def save_memory_tool(req: MemoryRequest, x_api_key: str = Header(None)):
    verify_key(x_api_key)
    save_memory(req.user_id, req.key, req.value)
    return {"tool": "save_memory", "status": "saved"}


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
# MCP ENDPOINT (IMPORTANT PART)
# =========================

@app.post("/mcp")
async def mcp_handler(request: Request, x_api_key: str = Header(None)):
    verify_key(x_api_key)

    body = await request.json()
    method = body.get("method")

    # -------------------------
    # LIST TOOLS
    # -------------------------
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "get_student",
                    "description": "Get student details",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "student_id": {"type": "string"}
                        },
                        "required": ["student_id"]
                    }
                },
                {
                    "name": "save_memory",
                    "description": "Save memory for user",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string"},
                            "key": {"type": "string"},
                            "value": {}
                        },
                        "required": ["user_id", "key", "value"]
                    }
                },
                {
                    "name": "get_memory",
                    "description": "Get user memory",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string"}
                        },
                        "required": ["user_id"]
                    }
                }
            ]
        }

    # -------------------------
    # EXECUTE TOOL
    # -------------------------
    if method == "tools/call":
        tool = body["params"]["name"]
        args = body["params"]["arguments"]

        if tool == "get_student":
            return {
                "result": get_student_logic(args["student_id"])
            }

        if tool == "save_memory":
            save_memory(args["user_id"], args["key"], args["value"])
            return {"result": "saved"}

        if tool == "get_memory":
            return {
                "result": get_memory(args["user_id"])
            }

        return {"error": "unknown tool"}

    return {"error": "invalid method"}


# =========================
# BASIC ENDPOINTS
# =========================

@app.get("/")
def home():
    return {"message": "MCP Server Running 🚀"}

@app.get("/health")
def health():
    return {"status": "ok"}
