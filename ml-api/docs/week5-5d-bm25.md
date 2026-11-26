# Week 5D — BM25 (keyword retrieval)

**One idea:** rank documents by **word overlap** (BM25), not by embedding “meaning.” Same corpus, different scoring.

Code: `app/retrieval/bm25.py` · build: `python -m app.retrieval.build_bm25` · compare: `scripts/practice_5d_bm25_vs_vector.py`.

---

## 1. Keyword vs vector (one table)

| | BM25 (keyword) | Vector (embeddings) |
|--|----------------|---------------------|
| Matches | shared terms / IDs | similar meaning / paraphrase |
| Needs | tokenizer + term stats | embedding model + vectors |
| Strong at | `CorpWiFi`, error codes, exact names | “can’t get on the network from home” |
| Weak at | synonyms with no shared words | rare exact tokens if paraphrased away |

Neither replaces the other. That is why hybrid exists (5E).

---

## 2. BM25 in plain terms

BM25 is a classic search ranking formula (Elasticsearch / Lucene family):

- words that appear in the **query and the doc** help the score;
- very common words help less (like a soft IDF);
- longer docs are adjusted so length alone does not win.

You do **not** need the full formula memorized for this week. You need: **it’s lexical scoring, not a neural embedding.**

Laravel / ES analogy: closer to Elasticsearch `match` query than to cosine over MiniLM.

---

## 3. Offline index (same spirit as 5B)

**Build (rare):** tokenize all docs → save `artifacts/retrieval/bm25_meta.json`.

**Search:** tokenize the query → BM25 scores vs saved token lists → top-k **documents**.

Still returns documents (ids + scores), not ticket classes.

Scores are on a **different scale** than cosine — do not compare `0.72` cosine to `4.1` BM25 as “which is more confident” without care.

---

## 4. What to watch in the practice script

The script runs the **same queries** through BM25 and vector side by side:

1. Exact term: `CorpWiFi` — expect keyword to shine.
2. Paraphrase VPN problem — expect vector to shine.
3. A mixed / noisy query — see disagreement.

Ask: for each query, which ranking would you trust for Internal Assistant?

---

## Check you “got” 5D

1. BM25 uses embeddings — true or false?
2. Name one query where keyword beats vector, and one where vector beats keyword.
3. Can you sort by “average of raw BM25 score and cosine” without thinking? Why / why not?

---

## Practice

```powershell
cd C:\Docker\ai\internal-assistant-project\ml-api
uv sync --extra retrieval
uv run python -m app.retrieval.build
uv run python -m app.retrieval.build_bm25
uv run python scripts/practice_5d_bm25_vs_vector.py
```
