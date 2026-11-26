# Retrieval — embeddings + cosine top-k

How Internal Assistant finds relevant wiki/runbook text **before** an LLM answers (RAG building block).

**Лекции:** [`retrieval-lecture.md`](retrieval-lecture.md) (кратко) · [`retrieval-deep-lecture.md`](retrieval-deep-lecture.md) (по источникам: RAG paper, ST, hybrid)

---

## 1. Goal

Given a user question, return the **top-k** corpus documents by semantic similarity.

Flow:

```
question → embedding model → vector
corpus docs → (once) embedding vectors on disk
compare with cosine → top-k docs
```

Same math as the toy cosine demo; vectors now come from a real model (~384 dimensions).

---

## 2. Concepts

### Embedding

A model maps text to a list of numbers (vector) so that **similar meaning → similar direction** in space.

Example model: `sentence-transformers/all-MiniLM-L6-v2` (CPU-friendly).

### Cosine similarity

\[
\cos(a,b) = (a·b) / (|a| |b|)
\]

We L2-normalize vectors at index/query time, so cosine = dot product.

| Score | Meaning |
|-------|---------|
| ~1.0 | very similar direction |
| ~0.0 | unrelated |
| low/negative | opposite / not useful |

### Top-k

Sort documents by score descending, take first k (usually 3–5 for RAG context).

### What this is not

- Not LLM generation / fine-tuning — **retrieve** only
- BM25 lives beside vectors: [`week5-5d-bm25.md`](week5-5d-bm25.md)

---

## 3. Layout

```
ml-api/
├── data/corpus/*.md              # short runbook docs
├── app/retrieval/
│   ├── corpus.py                 # load markdown
│   ├── index.py / search.py      # embeddings + cosine
│   ├── bm25.py                   # keyword BM25
│   ├── build.py / build_bm25.py
│   └── cli_search.py / cli_search_bm25.py
├── artifacts/retrieval/
│   ├── embeddings.npy + meta.json
│   └── bm25_meta.json
└── docs/RETRIEVAL.md
```

---

## 4. Setup

```powershell
cd C:\Docker\ai\internal-assistant-project\ml-api
uv sync --extra retrieval
```

First run downloads the embedding model (network required).

---

## 5. Build index (once, or after corpus changes)

```powershell
uv run python -m app.retrieval.build
```

Writes `artifacts/retrieval/embeddings.npy` and `meta.json`.

---

## 6. Search (vector)

```powershell
uv run python -m app.retrieval.cli_search "cannot connect to vpn"
uv run python -m app.retrieval.cli_search "new hire laptop" -k 5
```

## 6b. BM25 (keyword)

```powershell
uv run python -m app.retrieval.build_bm25
uv run python -m app.retrieval.cli_search_bm25 "CorpWiFi"
uv run python scripts/practice_5d_bm25_vs_vector.py
uv run python scripts/practice_5e_hybrid.py
```

Hybrid (RRF): [`week5-5e-hybrid-rag.md`](week5-5e-hybrid-rag.md) · [`hybrid-note.md`](hybrid-note.md)

Example hit shape (same fields; score scale differs):

```json
{
  "id": "vpn-reset.md",
  "score": 0.72,
  "path": "data/corpus/vpn-reset.md",
  "snippet": "# VPN reset ..."
}
```

---

## 7. How this feeds the product later

| Stage | Use |
|-------|-----|
| Now | vector + BM25 + hybrid RRF (`hybrid.py`) |
| Next | week 6 LLM gateway; week 7 `POST /ask` RAG |

---

## 8. Operational notes

- Rebuild index when corpus files change  
- Keep the **same** `model_name` for build and search  
- Chunking strategy matters later for long PDFs; here each `.md` is one chunk  
