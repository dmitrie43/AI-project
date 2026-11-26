# Week 5E — Hybrid retrieval + why RAG before the LLM

**One idea:** keyword and vector fail differently — fuse them; retrieval feeds the LLM facts so it invents less.

Code: `app/retrieval/hybrid.py` (`search_hybrid`, RRF) · practice: `scripts/practice_5e_hybrid.py` · note: [`hybrid-note.md`](hybrid-note.md).

---

## 1. When to use what

| Mode | Use when |
|------|----------|
| **Keyword (BM25)** | Exact IDs, product names, error codes (`CorpWiFi`) |
| **Vector** | Paraphrase, “same idea, different words” |
| **Hybrid** | Default for Internal Assistant — users mix both behaviors |

You already saw (5D): paraphrase → vector wins; exact token → BM25 wins. Hybrid aims to keep both wins.

---

## 2. Why not average raw scores?

BM25 scores can be `10+`. Cosine is roughly `0..1`. Averaging them is like mixing rubles and dollars.

**RRF (Reciprocal Rank Fusion)** ignores raw scores and uses **ranks**:

\[
\mathrm{RRF}(d) = \sum_{\text{lists}} \frac{1}{\mathrm{rrf\_k} + \mathrm{rank}(d)}
\]

Typical `rrf_k = 60`. Doc strong in either list rises; doc strong in both rises more.

---

## 3. Why retrieval before the LLM? (RAG)

The LLM does not magically know your private runbooks. Flow:

```
question → retrieve top-k docs → put them in the prompt → LLM answers with citations
```

| Without retrieval | With retrieval (RAG) |
|-------------------|----------------------|
| Guesses from training data | Grounds on *your* docs |
| Stale / wrong internal policy | Updatable by reindexing |
| Hard to cite | Can point at `vpn-reset.md` |

**RAG ≠ fine-tune:** RAG = fetch docs at ask-time. Fine-tune = change model weights (expensive, slow to update facts). Prefer RAG for internal wiki that changes often.

(Full LLM `POST /ask` is week 7 — here you only need the *why*.)

---

## Check you “got” 5E

1. When is hybrid better than vector-only?
2. Why RRF instead of averaging BM25 + cosine?
3. In one sentence: why retrieval before the LLM in Internal Assistant?

Read [`hybrid-note.md`](hybrid-note.md), run the practice script, then answer the three checks.

---

## Practice

```powershell
cd C:\Docker\ai\internal-assistant-project\ml-api
uv run python -m app.retrieval.build
uv run python -m app.retrieval.build_bm25
uv run python scripts/practice_5e_hybrid.py
```
