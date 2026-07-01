import json
import os
import re
import faiss
import numpy as np
import pdfplumber
from sentence_transformers import SentenceTransformer

GLOSSARY_PATH = os.path.join("core", "retail_analytics_metric_list.pdf")
INDEX_PATH    = os.path.join("data", "index.faiss")
CHUNKS_PATH   = os.path.join("data", "chunks.json")
MODEL_NAME    = "all-MiniLM-L6-v2"

# These are the exact metric header names in the PDF
METRIC_HEADERS = [
    "Customer Lifetime Value - Pre-Discount (LTV Gross)",
    "Customer Lifetime Value - Post-Discount (LTV Net)",
    "Return Rate",
    "Recent Purchase Activity",
    "Category Affinity",
]

def load_and_chunk(path):
    # Extract all text from all pages, deduplicated
    raw = ""
    seen_lines = set()
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            for line in text.split("\n"):
                if line.strip() and line.strip() not in seen_lines:
                    seen_lines.add(line.strip())
                    raw += line + "\n"

    # Split on metric headers
    pattern = "(" + "|".join(re.escape(h) for h in METRIC_HEADERS) + ")"
    parts = re.split(pattern, raw)

    chunks = []
    i = 1
    while i < len(parts) - 1:
        header  = parts[i].strip()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""
        chunk   = f"{header}\n{content}"
        if len(chunk) > 50:
            chunks.append(chunk)
        i += 2

    print(f"Loaded {len(chunks)} chunks")
    for i, c in enumerate(chunks):
        print(f"  Chunk {i+1}: {c[:60]}...")
    return chunks

def build_and_save_index(chunks):
    print(f"\nLoading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    print("Embedding chunks...")
    embeddings = model.encode(chunks, show_progress_bar=True)
    embeddings = np.array(embeddings).astype("float32")
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, INDEX_PATH)
    with open(CHUNKS_PATH, "w") as f:
        json.dump(chunks, f, indent=2)
    print(f"Done. {index.ntotal} vectors saved.")

if __name__ == "__main__":
    chunks = load_and_chunk(GLOSSARY_PATH)
    build_and_save_index(chunks)