# Week 5C — Top-k and the same model (A/A)

**One idea:** rank all docs by cosine similarity, keep the **k** best **documents**. Query and corpus must use the **same** embedding model.

Code: `app/retrieval/search.py` (`search`, `_cosine_matrix`) · CLI: `python -m app.retrieval.cli_search`.

---

## 1. What top-k means

After you have one score per document:

```
sort scores high → low
take the first k rows
```

| k | Meaning |
|---|--------|
| 1 | single best guess (good for demos) |
| 3–5 | typical RAG context window filler |
| large | more recall, more noise / tokens later |

`k` is **not** “number of classes.” It is “how many wiki/runbook chunks to return.”

Search returns things like `vpn-reset.md` + score — **not** `is_open=0.87`. That is `/predict`.

---

## 2. Pipeline in one glance

```
query text
  → encode with model from meta.json     # only the query (5B)
  → cosine vs every row in embeddings.npy
  → argsort descending
  → first k docs from meta["docs"]
```

In code, with normalized vectors, cosine ≈ **dot product** (`doc_matrix @ q`).

---

## 3. Same model A/A (critical)

| Setup | OK? |
|-------|-----|
| Docs: MiniLM, query: MiniLM | Yes |
| Docs: model A, query: model B | No — different spaces |

The index stores `model_name` so search reloads **that** encoder. Mixing models makes scores look like numbers but mean nothing.

---

## 4. Good query vs weak query

Semantic search helps with paraphrase (“can’t get on the VPN” ≈ VPN reset doc).

It can still fail when:

- the question is vague (“help”), or
- the right answer needs an exact code/ID (BM25 territory — 5D), or
- nothing in the corpus matches (top-1 is still “best of a bad set”).

Always look at **score + snippet**, not only rank 1.

---

## Check you “got” 5C

1. What does `k=1` return — a ticket class or a document?
2. Why must query and docs share one embedding model?
3. If you raise `k` from 1 to 5, what do you gain / risk?

Then run the practice script.

---

## Practice

```powershell
cd C:\Docker\ai\internal-assistant-project\ml-api
uv run python -m app.retrieval.build   # if index missing
uv run python scripts/practice_5c_topk.py
```

Also try by hand:

```powershell
uv run python -m app.retrieval.cli_search "cannot connect to vpn" -k 1
uv run python -m app.retrieval.cli_search "cannot connect to vpn" -k 3
uv run python -m app.retrieval.cli_search "asdf qwerty" -k 3
```
