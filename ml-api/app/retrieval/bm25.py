"""BM25 (keyword) index build/load/search over the markdown corpus."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from app.retrieval.corpus import CORPUS_DIR, load_corpus
from app.retrieval.index import ARTIFACT_DIR, ROOT

BM25_META_PATH = ARTIFACT_DIR / "bm25_meta.json"
_TOKEN_RE = re.compile(r"[a-z0-9_]+", re.IGNORECASE)


def tokenize(text: str) -> list[str]:
    """Simple whitespace/alnum tokenizer — enough for this lab."""
    return _TOKEN_RE.findall(text.lower())


def build_bm25(
    *,
    corpus_dir: Path = CORPUS_DIR,
    artifact_dir: Path = ARTIFACT_DIR,
) -> dict[str, Any]:
    docs = load_corpus(corpus_dir)
    tokenized = [tokenize(d["text"]) for d in docs]
    artifact_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "doc_count": len(docs),
        "tokenizer": "alnum_lower",
        "docs": [
            {
                "id": d["id"],
                "path": d["path"],
                "text": d["text"],
                "tokens": toks,
            }
            for d, toks in zip(docs, tokenized, strict=True)
        ],
    }
    path = artifact_dir / "bm25_meta.json"
    path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"doc_count": len(docs), "meta_path": str(path.relative_to(ROOT))}


def load_bm25(*, artifact_dir: Path = ARTIFACT_DIR) -> dict[str, Any]:
    from rank_bm25 import BM25Okapi

    meta_path = artifact_dir / "bm25_meta.json"
    if not meta_path.is_file():
        raise FileNotFoundError(
            f"BM25 index not found under {artifact_dir}. Run: uv run python -m app.retrieval.build_bm25"
        )
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    tokenized = [d["tokens"] for d in meta["docs"]]
    return {"meta": meta, "bm25": BM25Okapi(tokenized)}


def search_bm25(
    query: str,
    *,
    k: int = 3,
    index: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    idx = index or load_bm25()
    bm25 = idx["bm25"]
    docs = idx["meta"]["docs"]
    scores = bm25.get_scores(tokenize(query))
    top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    results: list[dict[str, Any]] = []
    for i in top_idx:
        doc = docs[i]
        results.append(
            {
                "id": doc["id"],
                "score": float(scores[i]),
                "path": doc["path"],
                "snippet": doc["text"][:240].replace("\n", " "),
            }
        )
    return results
