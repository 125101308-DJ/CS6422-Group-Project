# build_index.py
import pandas as pd
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from pathlib import Path

CSV_PATH = "/Users/harinisri/Documents/Restraurant-project/cleaned_restaurant_data.csv"   
INDEX_DIR = Path("index_data")
INDEX_DIR.mkdir(exist_ok=True)

# Load dataset
df = pd.read_csv(CSV_PATH, dtype=str).fillna("")

# helper to make a single descriptive text for a restaurant row
def row_to_text(row):
    # Using the exact column names the user provided
    name = row.get("name", "")
    place_id = row.get("place_id", "")
    rtype = row.get("restaurant_type", "")
    cuisine = row.get("cuisine_type", "")
    address = row.get("address", "")
    rating = row.get("rating", "")
    review_count = row.get("review_count", "")
    lat = row.get("latitude", "")
    lon = row.get("longitude", "")
    price_range = row.get("price_range", "")
    website = row.get("website", "")
    url = row.get("url", "")
    atmosphere = row.get("atmosphere", "")
    amenities = row.get("amenities", "")

    text = (
        f"{name} (place_id: {place_id}). Type: {rtype}. Cuisine: {cuisine}. "
        f"Address: {address}. Rating: {rating} ({review_count} reviews). "
        f"Price range: {price_range}. Atmosphere: {atmosphere}. Amenities: {amenities}. "
        f"Website: {website}. Map URL: {url}. Coordinates: {lat}, {lon}."
    )
    return text

# Build texts list and metadata
texts = []
meta = []
for _, row in df.iterrows():
    t = row_to_text(row.to_dict())
    texts.append(t)
    meta.append({
        "name": row.get("name", ""),
        "place_id": row.get("place_id", ""),
        "address": row.get("address", ""),
        "cuisine_type": row.get("cuisine_type", ""),
        "rating": row.get("rating", ""),
        "price_range": row.get("price_range", ""),
        "atmosphere": row.get("atmosphere", ""),
        "amenities": row.get("amenities", ""),
        "raw_row": row.to_dict()
    })

# Create embeddings
print("Loading embedding model...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")
print("Creating embeddings...")
embeddings = embedder.encode(texts, show_progress_bar=True, convert_to_numpy=True)

# Save embeddings to FAISS
d = embeddings.shape[1]
index = faiss.IndexFlatL2(d)
index.add(embeddings)
faiss.write_index(index, str(INDEX_DIR / "faiss_index.bin"))
np.save(INDEX_DIR / "texts.npy", np.array(texts, dtype=object))
with open(INDEX_DIR / "meta.jsonl", "w", encoding="utf-8") as fout:
    for m in meta:
        fout.write(json.dumps(m) + "\n")

print("Index built and saved to", INDEX_DIR)
