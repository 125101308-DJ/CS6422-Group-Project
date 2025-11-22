import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import requests
import time

INDEX_DIR = Path("index_data")
EMBED_MODEL = "all-MiniLM-L6-v2"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3:latest"  # or the model you have pulled with ollama

print("Loading index and metadata...")
index = faiss.read_index("faiss_index.bin")
texts = np.load("texts.npy", allow_pickle=True)
meta = [json.loads(line) for line in open("meta.jsonl", "r", encoding="utf-8").read().splitlines()]

print("Loading embedding model...")
embedder = SentenceTransformer(EMBED_MODEL)
print("✓ Embedding model loaded successfully")

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

A: 
"""

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

def generate_reply(prompt, max_new_tokens=256, temperature=0.2):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_new_tokens,
                    "top_p": 0.95
                }
            },
            timeout=120
        )
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        else:
            error_msg = f"Ollama API error: {response.status_code}"
            print(error_msg)
            return f"Error: {error_msg}"
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to connect to Ollama: {e}"
        print(error_msg)
        return "Error: Ollama service not running. Please start Ollama and try again."

def get_chatbot_response(user_query, session_history=None, top_k=5):
    user_context = ""
    if session_history:
        history_tail = session_history[-6:]
        hist_text = []
        for msg in history_tail:
            role = msg.get("role", "user")
            hist_text.append(f"{role.upper()}: {msg.get('text','')}")
        user_context = "\n".join(hist_text)

    retrieved = retrieve(user_context + "\n" + user_query, top_k=top_k)
    records_block = format_records_for_prompt(retrieved) if retrieved else "No matching records found."

    prompt = PROMPT_TEMPLATE.format(
        system=SYSTEM_INSTRUCTION,
        user=user_query,
        records=records_block
    )

    start = time.time()
    reply = generate_reply(prompt, max_new_tokens=300, temperature=0.2)
    latency = time.time() - start

    return {
        "reply": reply,
        "retrieved": [r["meta"] for r in retrieved],
        "latency_seconds": latency
    }

if __name__ == "__main__":
    print("\n🧪 Testing chatbot engine...\n")
    test_q = "Recommend affordable Irish cafes in Cork with casual atmosphere and near Blackpool"
    out = get_chatbot_response(test_q, session_history=[
        {"role":"user","text":"I'm looking for a casual cafe."},
        {"role":"assistant","text":"Sure — do you have a location in mind?"}
    ])
    print(json.dumps(out, indent=2))
