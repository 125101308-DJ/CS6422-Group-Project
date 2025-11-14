# inference_api.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
import time
from chatbot_engine import get_chatbot_response

app = FastAPI(title="Restaurant Chatbot Inference API")

# Simple in-memory session store: replace with Redis for production
SESSIONS = {}  # { session_id: {"history":[{"role":..., "text":...}], "last_active": timestamp} }
SESSION_TIMEOUT = 60 * 60 * 2  # 2 hours

class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    # create session if not provided
    session_id = req.session_id or str(uuid.uuid4())
    message = req.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # init session
    if session_id not in SESSIONS:
        SESSIONS[session_id] = {"history": [], "last_active": time.time()}

    # append user message to history
    SESSIONS[session_id]["history"].append({"role": "user", "text": message})
    SESSIONS[session_id]["last_active"] = time.time()

    # get response from engine (passes history to allow followups)
    engine_out = get_chatbot_response(message, session_history=SESSIONS[session_id]["history"], top_k=5)

    # append assistant response to history
    SESSIONS[session_id]["history"].append({"role": "assistant", "text": engine_out["reply"]})
    SESSIONS[session_id]["last_active"] = time.time()

    # cleanup old sessions periodically (simple)
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
    return {"status": "ok"}

# You can run: uvicorn inference_api:app --host 0.0.0.0 --port 8000
