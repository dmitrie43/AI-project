"""Load markdown corpus from disk."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORPUS_DIR = ROOT / "data" / "corpus"


def load_corpus(corpus_dir: Path = CORPUS_DIR) -> list[dict[str, str]]:
    docs: list[dict[str, str]] = []
    for path in sorted(corpus_dir.glob("*.md")):
        docs.append(
            {
                "id": path.name,
                "path": str(path.relative_to(ROOT)),
                "text": path.read_text(encoding="utf-8").strip(),
            }
        )
    if not docs:
        raise FileNotFoundError(f"No markdown files in {corpus_dir}")
    return docs
