# Week 5B — Why build the index offline?

**One idea:** encode documents **once**, save vectors to disk; on each question encode **only the query**, then compare.

Code you already have: `app/retrieval/index.py` (`build_index` / `load_index`) + `search.py`.

---

## 1. The slow way (do not ship this)

Every user question:

```
load all docs → encode ALL of them with the model → encode question → cosine → top-k
```

Problems:

- The embedding model is the expensive step (CPU/GPU, seconds on a big corpus).
- You repeat the same work for every question even when docs did not change.
- Latency and cost grow with corpus size, not with question length.

Laravel analogy: like running a full-table `SELECT` and recomputing a heavy derived column on **every** HTTP request instead of caching the derived data.

---

## 2. The normal way (offline index)

**Offline (build, rare):**

```
docs → model.encode(docs) → embeddings.npy + meta.json
```

**Online (search, every question):**

```
question → model.encode(question) → cosine vs saved matrix → top-k docs
```

| When | What runs |
|------|-----------|
| Corpus added/changed | `build` again |
| User asks a question | encode **1** text + cheap matrix math |

That saved matrix + metadata **is** the retrieval index in this project (not a MySQL B-tree — same *purpose*: pay once, query fast).

---

## 3. What the files mean

| File | Role |
|------|------|
| `artifacts/retrieval/embeddings.npy` | Matrix `[n_docs × dim]` — one row per document |
| `artifacts/retrieval/meta.json` | Doc ids, paths, texts, `model_name`, dim |

Row `i` in the matrix belongs to `meta["docs"][i]`. Never reorder one without the other.

---

## 4. Same model, always

`meta.json` stores `model_name`. Search must load **that** model for the query.  
Different model ⇒ different space ⇒ scores are garbage (you covered this in 5A / quiz).

---

## 5. When to rebuild

Rebuild when:

- you add/edit/delete corpus files, or
- you change embedding model / normalize settings.

No rebuild needed for a new user question alone.

---

## Check you “got” 5B

In your own words:

1. What is expensive: encoding docs or the cosine dot products?
2. What does `search` encode — all docs, or only the query?
3. How is this like (and unlike) a database index?

Then run the practice script below.

---

## Practice

```powershell
cd C:\Docker\ai\internal-assistant-project\ml-api
uv sync --extra retrieval
uv run python -m app.retrieval.build
uv run python scripts/practice_5b_offline_index.py
```

Read the printed timings and the artifact shapes. Optional: open `meta.json` and confirm `doc_count` matches the matrix rows.
