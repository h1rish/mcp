from fastapi import FastAPI, Request, Header, HTTPException
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
# SIMPLE MEMORY
# =========================
memory_store: Dict[str, Dict[str, Any]] = {}

def save_memory(user_id: str, key: str, value: Any):
    memory_store.setdefault(user_id, {})[key] = value

def get_memory(user_id: str):
    return memory_store.get(user_id, {})


# =========================
# TOOL LOGIC
# =========================
def get_student(student_id: str):
    return {
        "id": student_id,
        "name": "John Doe",
        "course": "AI & ML",
        "marks": 85
    }


# =========================
# MCP ENDPOINT (ROBUST)
# =========================
@app.post("/mcp")
async def mcp(request: Request, x_api_key: str = Header(None)):
    verify_key(x_api_key)

    body = await request.json()

    method = body.get("method")
    req_id = body.get("id", 1)
    params = body.get("params", {})

    # =========================
    # tools/list
    # =========================
    if method == "tools/list":
        return {
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "get_student",
                        "description": "Get student details by ID",
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
                        "description": "Save user memory",
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
        }

    # =========================
    # tools/call
    # =========================
    if method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "get_student":
            return {
                "id": req_id,
                "result": get_student(args.get("student_id"))
            }

        if tool_name == "save_memory":
            save_memory(
                args.get("user_id"),
                args.get("key"),
                args.get("value")
            )
            return {
                "id": req_id,
                "result": {"status": "saved"}
            }

        if tool_name == "get_memory":
            return {
                "id": req_id,
                "result": get_memory(args.get("user_id"))
            }

    # =========================
    # fallback (important for Azure quirks)
    # =========================
    return {
        "id": req_id,
        "result": {
            "error": "Unknown method",
            "method_received": method
        }
    }


# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def home():
    return {"status": "MCP Server Running"}

@app.get("/health")
def health():
    return {"status": "ok"}
