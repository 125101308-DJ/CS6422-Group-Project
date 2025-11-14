# chatbot_engine.py
import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
import torch
import time

INDEX_DIR = Path("index_data")
EMBED_MODEL = "all-MiniLM-L6-v2"
# change model id if desired / available
MISTRAL_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# Load vector index and metadata
print("Loading index and metadata...")
index = faiss.read_index(str(INDEX_DIR / "faiss_index.bin"))
texts = np.load(INDEX_DIR / "texts.npy", allow_pickle=True)
meta = [json.loads(line) for line in open(INDEX_DIR / "meta.jsonl", "r", encoding="utf-8").read().splitlines()]

# Load embedding model
embedder = SentenceTransformer(EMBED_MODEL)

# Load Mistral model + tokenizer
print("Loading Mistral model (this may take a while)...")
tokenizer = AutoTokenizer.from_pretrained(MISTRAL_MODEL, use_fast=True)
# try efficient loading if bitsandbytes available and GPU present:
device = "cuda" if torch.cuda.is_available() else "cpu"

try:
    if device == "cuda":
        model = AutoModelForCausalLM.from_pretrained(
            MISTRAL_MODEL,
            device_map="auto",
            load_in_8bit=True,  # optional for memory saving
            torch_dtype=torch.float16,
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(MISTRAL_MODEL)
except Exception as e:
    print("Falling back to standard load due to:", e)
    model = AutoModelForCausalLM.from_pretrained(MISTRAL_MODEL)

model.to(device)
print(" Model loaded successfully on", device)
model.eval()

# Prompt template - we explicitly tell Mistral to use ONLY the provided context
SYSTEM_INSTRUCTION = (
    "You are a concise and helpful restaurant recommendation assistant. "
    "When given a user question and a list of restaurant records from a database, "
    "use only that provided information to answer. If the answer is not contained "
    "in the records, say you don't know and suggest how to refine the query. "
    "Always include 2-4 suggestions with a short reason and include the restaurant name and price/rating if available."
)

PROMPT_TEMPLATE = """SYSTEM: {system}

User: {user}

Database records:
{records}

Assistant: 
"""

# Utility: retrieve top_k relevant docs
def retrieve(user_query, top_k=5):
    q_emb = embedder.encode([user_query], convert_to_numpy=True)
    distances, idxs = index.search(q_emb, top_k)
    results = []
    for i in idxs[0]:
        if i < 0 or i >= len(texts):
            continue
        results.append({
            "text": texts[i],
            "meta": meta[i]
        })
    return results

# Build a compact text block from retrieval results for prompt
def format_records_for_prompt(retrieved):
    parts = []
    for i, r in enumerate(retrieved, start=1):
        m = r["meta"]
        parts.append(
            f"{i}. {m.get('name','')} | Cuisine: {m.get('cuisine_type','')} | "
            f"Address: {m.get('address','')} | Price: {m.get('price_range','')} | "
            f"Rating: {m.get('rating','')} | Atmosphere: {m.get('atmosphere','')} | Amenities: {m.get('amenities','')}"
        )
    return "\n".join(parts)

# Generate text from Mistral
def generate_reply(prompt, max_new_tokens=256, temperature=0.2):
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048).to(model.device)
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=True, temperature=temperature, top_p=0.95, eos_token_id=tokenizer.eos_token_id)
    text = tokenizer.decode(out[0], skip_special_tokens=True)
    # If the model repeats the prompt in returned text, strip prompt portion:
    return text[len(prompt):].strip() if text.startswith(prompt) else text.strip()

# High-level call used by API
def get_chatbot_response(user_query, session_history=None, top_k=5):
    # session_history: list of dicts [{"role":"user"/"assistant","text":...}, ...]
    # We include a small chat summary to give follow-up context
    user_context = ""
    if session_history:
        # include last 4 messages to provide followup capability
        history_tail = session_history[-6:]
        hist_text = []
        for msg in history_tail:
            role = msg.get("role", "user")
            hist_text.append(f"{role.upper()}: {msg.get('text','')}")
        user_context = "\n".join(hist_text)

    # 1) retrieve relevant restaurants
    retrieved = retrieve(user_context + "\n" + user_query, top_k=top_k)
    records_block = format_records_for_prompt(retrieved) if retrieved else "No matching records found."

    # 2) construct prompt
    prompt = PROMPT_TEMPLATE.format(system=SYSTEM_INSTRUCTION, user=user_query, records=records_block)

    # 3) generate text
    start = time.time()
    reply = generate_reply(prompt, max_new_tokens=300, temperature=0.2)
    latency = time.time() - start

    # 4) return structured response; include the retrieved records for the Java service to show if needed
    return {
        "reply": reply,
        "retrieved": [r["meta"] for r in retrieved],
        "latency_seconds": latency
    }

# Example local test
if __name__ == "__main__":
    test_q = "Recommend affordable Irish cafes in Cork with casual atmosphere and near Blackpool"
    out = get_chatbot_response(test_q, session_history=[
        {"role":"user","text":"I'm looking for a casual cafe."},
        {"role":"assistant","text":"Sure — do you have a location in mind?"}
    ])
    print(json.dumps(out, indent=2))
