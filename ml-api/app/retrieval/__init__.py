"""Mini vector retriever (embeddings + cosine top-k)."""

from app.retrieval.search import search
from app.retrieval.index import build_index, load_index

__all__ = ["build_index", "load_index", "search"]
