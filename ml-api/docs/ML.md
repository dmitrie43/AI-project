# ML — tabular ticket classifier

How classical ML is used in **Internal Assistant** (ml-api).  
This document is the source of truth for training, metrics, and artifacts.

**sklearn API (классы, аргументы, выходы):** [`sklearn-lecture.md`](sklearn-lecture.md)

---

## 1. Goal

Predict whether a support ticket is still **open** (including `in_progress`) vs already **resolved**.

| Label `is_open` | Meaning |
|-----------------|--------|
| `0` | `status = resolved` |
| `1` | `status ∈ {open, in_progress}` |

Features (known at prediction time — no leakage from the answer itself):

| Feature | Type | Notes |
|---------|------|--------|
| `category` | categorical | vpn, access, hardware, … |
| `priority` | numeric | 1–5; missing → median impute |
| `satisfaction` | numeric | may be empty on open tickets |
| `tag_count` | numeric | number of tags |

We do **not** use `status` as a feature (that would be the answer).

---

## 2. Concepts (short)

### Baseline (majority class)

A dumb rule: always predict the most frequent label on the training set.

If the model does not beat this baseline on validation metrics, it is not useful.

See also product math notes: baseline / precision-recall / train-val.

### Train / validation split

- **train** — fit the model  
- **val** — measure quality on rows the model did not train on  

We use stratified 80/20 split (`random_state=42`) so class balance is preserved.

### Metrics

| Metric | Meaning |
|--------|---------|
| **Accuracy** | Share of correct predictions (misleading under imbalance) |
| **Precision** | Of predicted “open”, how many are really open |
| **Recall** | Of all real “open”, how many we caught |
| **F1** | Balance of precision and recall |

For rare “open” tickets, prefer **F1 / recall**, not accuracy alone.

### Logistic regression

Linear model on engineered features: weighted sum of (one-hot category + numeric fields) → class probability.  
Simple, fast, good first production baseline before trying boosting.

### Overfitting

If train metrics look perfect but val metrics collapse, the model memorized train.  
Always report **val** metrics (and keep a held-out test set later for final claims).

---

## 3. Layout

```
ml-api/
├── data/raw/tickets.csv      # source table
├── app/ml/train.py           # training entrypoint
├── artifacts/
│   ├── model.joblib          # sklearn pipeline
│   └── metrics.json          # baseline + model scores
└── docs/ML.md                # this file
```

---

## 4. Train

From `ml-api/`:

```powershell
uv sync
uv run python -m app.ml.train
```

Expected console summary: baseline vs model accuracy/F1, paths to artifacts.

### What the script does

1. Load CSV, build `is_open` from `status`  
2. Split train/val  
3. Score **majority baseline** on val  
4. Fit `OneHotEncoder + imputer + LogisticRegression` pipeline  
5. Score model on val (accuracy, precision, recall, F1)  
6. Save `artifacts/model.joblib` and `artifacts/metrics.json`

---

## 5. Read metrics

Open `artifacts/metrics.json` after training:

- `baseline_majority` — floor  
- `model_logistic` — current model on val  
- `beats_baseline_accuracy` / `beats_baseline_f1` — quick go/no-go flags  

Re-train after changing data or features; commit updated artifacts when the team agrees on a release candidate.

---

## 6. Inference API

Model is loaded at API startup from `artifacts/model.joblib`.

### `POST /predict`

Request:

```json
{
  "category": "vpn",
  "priority": 5,
  "satisfaction": null,
  "tag_count": 2
}
```

Response:

```json
{
  "prediction": 1,
  "label": "open_or_in_progress",
  "probabilities": { "0": 0.31, "1": 0.69 },
  "features_used": ["category", "priority", "satisfaction", "tag_count"]
}
```

### `GET /metrics`

Returns the contents of `artifacts/metrics.json` (baseline + model scores).

OpenAPI: http://127.0.0.1:8000/docs

### Debug `predict_one` locally

```powershell
cd ml-api
uv run python scripts/debug_predict.py
```

Or F5 → **Debug predict_one** (see `.vscode/launch.json`). Set a breakpoint in `app/ml/model_store.py` inside `predict_one`.

---

## 7. Operational notes

- Keep training reproducible: fixed `random_state`, pinned dependencies in `uv.lock`  
- Do not put future fields (`closed_at`, final `status`) into features  
- Log train job version + `metrics.json` hash when promoting a model  
