"""
Week 5E practice: BM25 vs vector vs hybrid (RRF).

Run from ml-api root:
  uv run python -m app.retrieval.build
  uv run python -m app.retrieval.build_bm25
  uv run python scripts/practice_5e_hybrid.py
"""

from __future__ import annotations

from app.retrieval.bm25 import search_bm25
from app.retrieval.hybrid import search_hybrid
from app.retrieval.search import search

QUERIES = [
    "CorpWiFi",
    "I cannot reach the company network from home",
    "VPN will not connect reset",
]


def _fmt(hits: list[dict]) -> str:
    return " | ".join(f"{h['id']}({h['score']:.3f})" for h in hits)


def main() -> None:
    print("Hybrid score is RRF (rank-based), not cosine or BM25.\n")
    for query in QUERIES:
        print(f"=== query: {query!r} ===")
        print(f"  BM25:    {_fmt(search_bm25(query, k=3))}")
        print(f"  Vector:  {_fmt(search(query, k=3))}")
        print(f"  Hybrid:  {_fmt(search_hybrid(query, k=3))}")
        print()

    print("=== Takeaway ===")
    print("  Hybrid keeps exact-token and paraphrase wins without mixing raw score scales.")
    print("  Next product step (week 7): feed these docs into an LLM prompt + citations.")


if __name__ == "__main__":
    main()
