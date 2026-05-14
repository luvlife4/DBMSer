from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from agent.agent import DBMSerAgent

app = FastAPI()
agent = DBMSerAgent()

class ChatRequest(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
def home():
    return Path("static/index.html").read_text(encoding="utf-8")

@app.post("/chat")
def chat(req: ChatRequest):
    reply = agent.agent_loop(req.message)
    return {"reply": reply}

@app.post("/new-chat")
def new_chat():
    global agent
    agent = DBMSerAgent()
    return {"ok": True}

@app.post("/learning-portrait")
def learning_portrait():
    report = agent.collect_mem()
    return {"report": report}

@app.post("/learning-schedule")
def store_schedule():
    schedule = agent.collect_schedule()
    return {"schedule":schedule}

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
