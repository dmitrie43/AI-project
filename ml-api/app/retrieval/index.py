"""Build and load embedding index artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from app.retrieval.corpus import CORPUS_DIR, load_corpus

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = ROOT / "artifacts" / "retrieval"
META_PATH = ARTIFACT_DIR / "meta.json"
EMB_PATH = ARTIFACT_DIR / "embeddings.npy"

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def build_index(
    *,
    corpus_dir: Path = CORPUS_DIR,
    model_name: str = DEFAULT_MODEL,
    artifact_dir: Path = ARTIFACT_DIR,
) -> dict[str, Any]:
    from sentence_transformers import SentenceTransformer

    docs = load_corpus(corpus_dir)
    texts = [d["text"] for d in docs]

    model = SentenceTransformer(model_name)
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
        convert_to_numpy=True,
    )
    embeddings = np.asarray(embeddings, dtype=np.float32)

    artifact_dir.mkdir(parents=True, exist_ok=True)
    np.save(EMB_PATH if artifact_dir == ARTIFACT_DIR else artifact_dir / "embeddings.npy", embeddings)

    meta = {
        "model_name": model_name,
        "doc_count": len(docs),
        "embedding_dim": int(embeddings.shape[1]),
        "normalized": True,
        "docs": [{"id": d["id"], "path": d["path"], "text": d["text"]} for d in docs],
    }
    meta_path = META_PATH if artifact_dir == ARTIFACT_DIR else artifact_dir / "meta.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "doc_count": len(docs),
        "embedding_dim": int(embeddings.shape[1]),
        "model_name": model_name,
        "embeddings_path": str(EMB_PATH.relative_to(ROOT)),
        "meta_path": str(META_PATH.relative_to(ROOT)),
    }


def load_index(
    *,
    artifact_dir: Path = ARTIFACT_DIR,
) -> dict[str, Any]:
    meta_path = artifact_dir / "meta.json"
    emb_path = artifact_dir / "embeddings.npy"
    if not meta_path.is_file() or not emb_path.is_file():
        raise FileNotFoundError(
            f"Index not found under {artifact_dir}. Run: uv run python -m app.retrieval.build"
        )
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    embeddings = np.load(emb_path)
    return {
        "meta": meta,
        "embeddings": embeddings,
        "model_name": meta["model_name"],
    }
