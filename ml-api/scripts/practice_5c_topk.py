"""
Week 5C practice: top-k results and same-model rule.

Run from ml-api root:
  uv run python -m app.retrieval.build   # if needed
  uv run python scripts/practice_5c_topk.py
"""

from __future__ import annotations

from app.retrieval.index import DEFAULT_MODEL, load_index
from app.retrieval.search import search


def _print_hits(title: str, query: str, k: int) -> None:
    hits = search(query, k=k)
    print(f"=== {title} ===")
    print(f"  query={query!r}  k={k}")
    for rank, h in enumerate(hits, start=1):
        print(f"  #{rank}  score={h['score']:.3f}  id={h['id']}")
        print(f"       snippet={h['snippet'][:100]}...")
    print()


def main() -> None:
    idx = load_index()
    meta = idx["meta"]
    model_name = meta["model_name"]

    print("=== Same model A/A ===")
    print(f"  index model_name: {model_name}")
    print(f"  DEFAULT_MODEL:    {DEFAULT_MODEL}")
    print("  search() loads model_name from the index for the query encode.")
    print("  Docs and query must stay in this one space — never mix model B.\n")

    good = "cannot connect to vpn"
    _print_hits("Good query, k=1 (one document, not a class)", good, k=1)
    _print_hits("Same query, k=3 (more context candidates)", good, k=3)

    weak = "asdf qwerty help"
    _print_hits("Weak / off-corpus query, k=3 (still returns something)", weak, k=3)

    print("=== Takeaway ===")
    print("  k = how many documents to return, sorted by cosine.")
    print("  Rank 1 is 'best match in this corpus', not 'correct answer guaranteed'.")
    print("  Output shape is doc id + score + snippet — not predict_proba classes.")


if __name__ == "__main__":
    main()
