from fastapi import FastAPI, Header, HTTPException, Request
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
# MCP ENDPOINT (FOUNDARY-COMPATIBLE)
# =========================
@app.post("/mcp")
async def mcp_handler(request: Request, x_api_key: str = Header(None)):
    verify_key(x_api_key)

    body = await request.json()
    method = body.get("method")
    req_id = body.get("id", 1)

    # -------------------------
    # LIST TOOLS
    # -------------------------
    if method == "tools/list":
        return {
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "get_student",
                        "description": "Fetch student details by student_id"
                    },
                    {
                        "name": "save_memory",
                        "description": "Save user memory key-value pair"
                    },
                    {
                        "name": "get_memory",
                        "description": "Retrieve user memory"
                    }
                ]
            }
        }

    # -------------------------
    # CALL TOOL
    # -------------------------
    if method == "tools/call":
        params = body.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})

        # ---- get_student ----
        if tool_name == "get_student":
            return {
                "id": req_id,
                "result": get_student(args["student_id"])
            }

        # ---- save_memory ----
        if tool_name == "save_memory":
            save_memory(args["user_id"], args["key"], args["value"])
            return {
                "id": req_id,
                "result": {"status": "saved"}
            }

        # ---- get_memory ----
        if tool_name == "get_memory":
            return {
                "id": req_id,
                "result": get_memory(args["user_id"])
            }

    # -------------------------
    # UNKNOWN METHOD
    # -------------------------
    return {
        "id": req_id,
        "error": f"Unknown method: {method}"
    }


# =========================
# BASIC ENDPOINTS
# =========================
@app.get("/")
def home():
    return {"message": "MCP Server Running 🚀"}

@app.get("/health")
def health():
    return {"status": "ok"}
