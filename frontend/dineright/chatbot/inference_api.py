from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
import time
from chatbot_engine import get_chatbot_response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Restaurant Chatbot Inference API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSIONS = {}
SESSION_TIMEOUT = 60 * 60 * 2

class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    message = req.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    if session_id not in SESSIONS:
        SESSIONS[session_id] = {"history": [], "last_active": time.time()}
    SESSIONS[session_id]["history"].append({"role": "user", "text": message})
    SESSIONS[session_id]["last_active"] = time.time()
    engine_out = get_chatbot_response(message, session_history=SESSIONS[session_id]["history"], top_k=5)
    SESSIONS[session_id]["history"].append({"role": "assistant", "text": engine_out["reply"]})
    SESSIONS[session_id]["last_active"] = time.time()
    now = time.time()
    stale = [sid for sid, s in SESSIONS.items() if now - s["last_active"] > SESSION_TIMEOUT]
    for sid in stale:
        del SESSIONS[sid]
    return JSONResponse({
        "session_id": session_id,
        "reply": engine_out["reply"],
        "retrieved": engine_out["retrieved"],
        "latency_seconds": engine_out["latency_seconds"]
    })

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Restaurant Chatbot API is running"}

@app.get("/")
async def root():
    return {
        "name": "Restaurant Chatbot API",
        "version": "1.0",
        "endpoints": {
            "chat": "POST /chat",
            "health": "GET /health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
