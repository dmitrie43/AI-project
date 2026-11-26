"""
Train tabular classifier for Internal Assistant.

Usage (from ml-api/):
  uv sync
  uv run python -m app.ml.train

Writes:
  artifacts/model.joblib
  artifacts/metrics.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.dummy import DummyClassifier

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "raw" / "tickets.csv"
ARTIFACTS_DIR = ROOT / "artifacts"
MODEL_PATH = ARTIFACTS_DIR / "model.joblib"
METRICS_PATH = ARTIFACTS_DIR / "metrics.json"

TARGET = "is_open"
CATEGORICAL = ["category"]
NUMERIC = ["priority", "satisfaction", "tag_count"]
FEATURE_COLS = CATEGORICAL + NUMERIC
RANDOM_STATE = 42
TEST_SIZE = 0.2


def load_dataset(path: Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Label: ticket still open / in progress (not resolved)
    df[TARGET] = df["status"].isin(["open", "in_progress"]).astype(int)
    return df


def build_pipeline() -> Pipeline:
    preprocess = ColumnTransformer(
        transformers=[
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL,
            ),
            (
                "num",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                    ]
                ),
                NUMERIC,
            ),
        ]
    )
    clf = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE)
    return Pipeline(steps=[("preprocess", preprocess), ("clf", clf)])


def majority_baseline_metrics(y_train: pd.Series, y_val: pd.Series) -> dict[str, Any]:
    """Always predict the most frequent class on train (baseline without ML)."""
    import numpy as np

    baseline = DummyClassifier(strategy="most_frequent")
    x_train = np.zeros((len(y_train), 1))
    x_val = np.zeros((len(y_val), 1))
    baseline.fit(x_train, y_train)
    pred = baseline.predict(x_val)
    majority_class = int(y_train.value_counts().index[0])
    return {
        "strategy": "most_frequent",
        "majority_class": majority_class,
        "majority_share_train": float((y_train == majority_class).mean()),
        "accuracy": float(accuracy_score(y_val, pred)),
        "precision": float(precision_score(y_val, pred, zero_division=0)),
        "recall": float(recall_score(y_val, pred, zero_division=0)),
        "f1": float(f1_score(y_val, pred, zero_division=0)),
    }


def model_metrics(y_true: pd.Series, y_pred: Any) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }


def train() -> dict[str, Any]:
    df = load_dataset()
    x = df[FEATURE_COLS]
    y = df[TARGET]

    x_train, x_val, y_train, y_val = train_test_split(
        x,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    baseline = majority_baseline_metrics(y_train, y_val)

    pipe = build_pipeline()
    pipe.fit(x_train, y_train)
    pred = pipe.predict(x_val)
    model = model_metrics(y_val, pred)

    report = classification_report(y_val, pred, output_dict=True, zero_division=0)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "pipeline": pipe,
            "feature_columns": FEATURE_COLS,
            "categorical": CATEGORICAL,
            "numeric": NUMERIC,
            "target": TARGET,
            "label_meaning": {
                "0": "resolved",
                "1": "open_or_in_progress",
            },
        },
        MODEL_PATH,
    )

    payload: dict[str, Any] = {
        "dataset": {
            "path": str(DATA_PATH.relative_to(ROOT)),
            "rows": int(len(df)),
            "target": TARGET,
            "features": FEATURE_COLS,
            "positive_rate": float(y.mean()),
        },
        "split": {
            "test_size": TEST_SIZE,
            "random_state": RANDOM_STATE,
            "train_rows": int(len(x_train)),
            "val_rows": int(len(x_val)),
        },
        "baseline_majority": baseline,
        "model_logistic": model,
        "beats_baseline_accuracy": bool(model["accuracy"] > baseline["accuracy"]),
        "beats_baseline_f1": bool(model["f1"] > baseline["f1"]),
        "classification_report": report,
        "artifacts": {
            "model": str(MODEL_PATH.relative_to(ROOT)),
            "metrics": str(METRICS_PATH.relative_to(ROOT)),
        },
    }

    METRICS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    metrics = train()
    print("Training complete.")
    print(f"Model:   {MODEL_PATH}")
    print(f"Metrics: {METRICS_PATH}")
    print(
        "Baseline accuracy={:.3f} F1={:.3f} | Model accuracy={:.3f} F1={:.3f}".format(
            metrics["baseline_majority"]["accuracy"],
            metrics["baseline_majority"]["f1"],
            metrics["model_logistic"]["accuracy"],
            metrics["model_logistic"]["f1"],
        )
    )


if __name__ == "__main__":
    main()
