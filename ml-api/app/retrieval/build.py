"""CLI: build embedding index.  uv run python -m app.retrieval.build"""

from __future__ import annotations

from app.retrieval.index import build_index


def main() -> None:
    info = build_index()
    print("Index built.")
    print(f"  docs:       {info['doc_count']}")
    print(f"  dim:        {info['embedding_dim']}")
    print(f"  model:      {info['model_name']}")
    print(f"  embeddings: {info['embeddings_path']}")
    print(f"  meta:       {info['meta_path']}")


if __name__ == "__main__":
    main()
