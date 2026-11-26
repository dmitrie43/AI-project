"""CLI: uv run python -m app.retrieval.build_bm25"""

from __future__ import annotations

import json

from app.retrieval.bm25 import build_bm25


def main() -> None:
    info = build_bm25()
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
