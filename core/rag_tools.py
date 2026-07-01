import json
import os
import numpy as np

INDEX_PATH  = os.path.join(os.path.dirname(__file__), "..", "data", "index.faiss")
CHUNKS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "chunks.json")
MODEL_NAME  = "all-MiniLM-L6-v2"
TOP_K       = 2

_model  = None
_index  = None
_chunks = None

def _load_resources():
    global _model, _index, _chunks
    if _model is not None:
        return
    if not os.path.exists(INDEX_PATH) or not os.path.exists(CHUNKS_PATH):
        raise FileNotFoundError("FAISS index not found. Run `python3 build_index.py` first.")
    import faiss
    from sentence_transformers import SentenceTransformer
    _model  = SentenceTransformer(MODEL_NAME)
    _index  = faiss.read_index(INDEX_PATH)
    with open(CHUNKS_PATH, "r") as f:
        _chunks = json.load(f)

METRIC_INDEX = [
    {"name": "LTV Gross (Customer Lifetime Value - Pre-Discount)", "description": "Total gross revenue at list price. Includes returned orders, excludes cancelled."},
    {"name": "LTV Net (Customer Lifetime Value - Post-Discount)",  "description": "Net revenue after discounts and after netting out refunds from returned orders."},
    {"name": "Return Rate",                                        "description": "Proportion of completed orders returned. Excludes cancellations from both numerator and denominator."},
    {"name": "Recent Purchase Activity (30/60/90-Day)",            "description": "Count of completed orders placed within 30, 60, or 90 days of a reference date."},
    {"name": "Category Affinity",                                  "description": "The category a customer buys most, and their concentration score. Excludes returned items."},
]

def list_metrics() -> dict:
    return {"success": True, "metrics": METRIC_INDEX, "count": len(METRIC_INDEX)}

def search_metrics(query: str) -> dict:
    if not query or not query.strip():
        return {"success": False, "error": "Query cannot be empty."}
    try:
        _load_resources()
        query_embedding = _model.encode([query])
        query_embedding = np.array(query_embedding).astype("float32")
        distances, indices = _index.search(query_embedding, TOP_K)
        results = []
        for rank, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx == -1:
                continue
            results.append({"rank": rank + 1, "score": round(float(dist), 4), "text": _chunks[idx]})
        return {"success": True, "query": query, "results": results}
    except FileNotFoundError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Search error: {str(e)}"}