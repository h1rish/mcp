from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "MCP Server is running"}

@app.get("/health")
def health():
    return {
        "status": "MCP Server Running",
        "framework": "FastAPI"
    }

@app.get("/student/{student_id}")
def student(student_id: str):
    return {
        "id": student_id,
        "name": "John Doe",
        "course": "AI & ML",
        "marks": 85
    }
