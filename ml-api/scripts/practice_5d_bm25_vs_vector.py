"""
Week 5D practice: BM25 (keyword) vs embedding top-k on the same queries.

Run from ml-api root:
  uv sync --extra retrieval
  uv run python -m app.retrieval.build
  uv run python -m app.retrieval.build_bm25
  uv run python scripts/practice_5d_bm25_vs_vector.py
"""

from __future__ import annotations

from app.retrieval.bm25 import search_bm25
from app.retrieval.search import search


QUERIES = [
    ("Exact token (keyword often wins)", "CorpWiFi"),
    ("Paraphrase (vector often wins)", "I cannot reach the company network from home"),
    ("Shared words both ways", "VPN will not connect reset"),
    ("Weak / garbage", "asdf qwerty"),
]


def _fmt(hits: list[dict], n: int = 3) -> str:
    parts = [f"{h['id']}({h['score']:.3f})" for h in hits[:n]]
    return " | ".join(parts)


def main() -> None:
    print("Scores are NOT on the same scale — compare ranks/ids, not raw numbers.\n")
    for title, query in QUERIES:
        print(f"=== {title} ===")
        print(f"  query: {query!r}")
        print(f"  BM25:    {_fmt(search_bm25(query, k=3))}")
        print(f"  Vector:  {_fmt(search(query, k=3))}")
        print()

    print("=== Takeaway ===")
    print("  BM25 = word overlap ranking (no embedding model).")
    print("  Vector = meaning / paraphrase.")
    print("  Pick by failure mode; hybrid (5E) combines both.")


if __name__ == "__main__":
    main()
