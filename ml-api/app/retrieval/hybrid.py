"""Hybrid retrieval: fuse BM25 + vector rankings with Reciprocal Rank Fusion (RRF)."""

from __future__ import annotations

from typing import Any

from app.retrieval.bm25 import search_bm25
from app.retrieval.search import search


def rrf_fuse(
    ranked_lists: list[list[dict[str, Any]]],
    *,
    k: int = 3,
    rrf_k: int = 60,
) -> list[dict[str, Any]]:
    """Merge several top-n rankings. Uses ranks only — safe across score scales."""
    scores: dict[str, float] = {}
    payload: dict[str, dict[str, Any]] = {}
    for results in ranked_lists:
        for rank, hit in enumerate(results, start=1):
            doc_id = hit["id"]
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (rrf_k + rank)
            # Prefer first-seen snippet/path; score overwritten below
            if doc_id not in payload:
                payload[doc_id] = {
                    "id": doc_id,
                    "path": hit["path"],
                    "snippet": hit["snippet"],
                }
    ordered = sorted(scores.keys(), key=lambda i: scores[i], reverse=True)[:k]
    out: list[dict[str, Any]] = []
    for doc_id in ordered:
        row = dict(payload[doc_id])
        row["score"] = float(scores[doc_id])
        out.append(row)
    return out


def search_hybrid(
    query: str,
    *,
    k: int = 3,
    candidate_k: int = 10,
    rrf_k: int = 60,
) -> list[dict[str, Any]]:
    """Run BM25 + vector, fuse with RRF, return top-k documents."""
    bm25_hits = search_bm25(query, k=candidate_k)
    vector_hits = search(query, k=candidate_k)
    return rrf_fuse([bm25_hits, vector_hits], k=k, rrf_k=rrf_k)
