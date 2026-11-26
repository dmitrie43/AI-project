"""CLI: uv run python -m app.retrieval.cli_search_bm25 "CorpWiFi" """

from __future__ import annotations

import argparse
import json

from app.retrieval.bm25 import search_bm25


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="BM25 top-k over keyword index")
    parser.add_argument("query", type=str)
    parser.add_argument("-k", type=int, default=3)
    args = parser.parse_args(argv)
    hits = search_bm25(args.query, k=args.k)
    print(json.dumps({"query": args.query, "hits": hits}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
