"""Query embedding + cosine top-k against the index."""

from __future__ import annotations

from typing import Any

import numpy as np

from app.retrieval.index import DEFAULT_MODEL, load_index


def _cosine_matrix(query_vec: np.ndarray, doc_matrix: np.ndarray) -> np.ndarray:
    """Docs are L2-normalized at index time; normalize query then dot = cosine."""
    q = np.asarray(query_vec, dtype=np.float32).reshape(-1)
    denom = float(np.linalg.norm(q))
    if denom == 0.0:
        return np.zeros(doc_matrix.shape[0], dtype=np.float32)
    q = q / denom
    return doc_matrix @ q


def search(
    query: str,
    *,
    k: int = 3,
    index: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    idx = index or load_index()
    meta = idx["meta"]
    embeddings: np.ndarray = idx["embeddings"]
    model_name = idx.get("model_name") or meta.get("model_name") or DEFAULT_MODEL

    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_name)
    q_vec = model.encode([query], normalize_embeddings=True, convert_to_numpy=True)[0]
    scores = _cosine_matrix(q_vec, embeddings)

    top_idx = np.argsort(scores)[::-1][:k]
    docs = meta["docs"]
    results: list[dict[str, Any]] = []
    for i in top_idx:
        doc = docs[int(i)]
        results.append(
            {
                "id": doc["id"],
                "score": float(scores[int(i)]),
                "path": doc["path"],
                "snippet": doc["text"][:240].replace("\n", " "),
            }
        )
    return results
