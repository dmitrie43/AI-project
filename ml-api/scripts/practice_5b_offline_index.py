"""
Week 5B practice: offline index vs encode-everything-per-query.

Run from ml-api root:
  uv run python -m app.retrieval.build
  uv run python scripts/practice_5b_offline_index.py
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    from sentence_transformers import SentenceTransformer

    from app.retrieval.corpus import load_corpus
    from app.retrieval.index import ARTIFACT_DIR, DEFAULT_MODEL, EMB_PATH, META_PATH, load_index

    query = "cannot connect to vpn"
    docs = load_corpus()
    texts = [d["text"] for d in docs]
    print(f"Corpus: {len(docs)} docs")
    print(f"Query:  {query!r}\n")

    # --- Inspect artifacts (must exist from build) ---
    if not EMB_PATH.is_file() or not META_PATH.is_file():
        raise SystemExit(
            f"Missing index under {ARTIFACT_DIR}.\n"
            "Run first: uv run python -m app.retrieval.build"
        )

    idx = load_index()
    matrix = idx["embeddings"]
    meta = idx["meta"]
    print("=== Offline artifacts ===")
    print(f"  embeddings.npy shape: {matrix.shape}  (rows=docs, cols=dim)")
    print(f"  model_name:           {meta['model_name']}")
    print(f"  doc_count in meta:    {meta['doc_count']}")
    print(f"  row 0 id:             {meta['docs'][0]['id']}")
    assert matrix.shape[0] == meta["doc_count"], "matrix rows must match meta docs"
    print("  OK: rows align with meta\n")

    model = SentenceTransformer(DEFAULT_MODEL)

    # --- Slow path demo: re-encode ALL docs for one query ---
    t0 = time.perf_counter()
    doc_vecs = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
    q_slow = model.encode([query], normalize_embeddings=True, convert_to_numpy=True)[0]
    scores_slow = doc_vecs @ (q_slow / np.linalg.norm(q_slow))
    top_slow = int(np.argmax(scores_slow))
    t_slow = time.perf_counter() - t0
    print("=== Naive (encode all docs + query every time) ===")
    print(f"  best:  {docs[top_slow]['id']}  score={float(scores_slow[top_slow]):.3f}")
    print(f"  time:  {t_slow:.2f}s\n")

    # --- Fast path: load matrix, encode query only ---
    t0 = time.perf_counter()
    loaded = load_index()
    q_fast = model.encode([query], normalize_embeddings=True, convert_to_numpy=True)[0]
    q_fast = q_fast / np.linalg.norm(q_fast)
    scores_fast = loaded["embeddings"] @ q_fast
    top_fast = int(np.argmax(scores_fast))
    t_fast = time.perf_counter() - t0
    print("=== Offline index (encode query only) ===")
    print(f"  best:  {loaded['meta']['docs'][top_fast]['id']}  score={float(scores_fast[top_fast]):.3f}")
    print(f"  time:  {t_fast:.2f}s\n")

    print("=== Takeaway ===")
    print("  Same winner expected; offline path skips re-encoding the corpus.")
    print(f"  Naive ~{t_slow:.2f}s vs offline ~{t_fast:.2f}s on this machine.")
    print("  Rebuild index only when docs or model change — not per question.")


if __name__ == "__main__":
    main()
