"""CLI: search corpus.  uv run python -m app.retrieval.cli_search "cannot connect vpn" """

from __future__ import annotations

import argparse
import json

from app.retrieval.search import search


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Cosine top-k over embedding index")
    parser.add_argument("query", type=str, help="Natural language query")
    parser.add_argument("-k", type=int, default=3, help="Top-k results")
    args = parser.parse_args(argv)

    hits = search(args.query, k=args.k)
    print(json.dumps({"query": args.query, "hits": hits}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
