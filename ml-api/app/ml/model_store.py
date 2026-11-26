"""Load and serve the trained joblib artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "artifacts" / "model.joblib"
METRICS_PATH = ROOT / "artifacts" / "metrics.json"

_bundle: dict[str, Any] | None = None


def model_path() -> Path:
    return MODEL_PATH


def metrics_path() -> Path:
    return METRICS_PATH


def load_model(path: Path | None = None) -> dict[str, Any]:
    global _bundle
    target = path or MODEL_PATH
    if not target.is_file():
        raise FileNotFoundError(
            f"Model artifact not found: {target}. Run: uv run python -m app.ml.train"
        )
    _bundle = joblib.load(target)
    return _bundle


def get_bundle() -> dict[str, Any]:
    if _bundle is None:
        return load_model()
    return _bundle


def predict_one(features: dict[str, Any]) -> dict[str, Any]:
    bundle = get_bundle()
    pipeline = bundle["pipeline"]
    feature_columns: list[str] = list(bundle["feature_columns"])
    label_meaning: dict[str, str] = dict(bundle.get("label_meaning", {}))

    row = {col: features.get(col) for col in feature_columns}
    frame = pd.DataFrame([row], columns=feature_columns)

    pred = int(pipeline.predict(frame)[0])
    proba = pipeline.predict_proba(frame)[0]
    classes = [int(c) for c in pipeline.named_steps["clf"].classes_]
    probabilities = {str(cls): float(p) for cls, p in zip(classes, proba, strict=True)}

    return {
        "prediction": pred,
        "label": label_meaning.get(str(pred), str(pred)),
        "probabilities": probabilities,
        "features_used": feature_columns,
    }


def read_metrics() -> dict[str, Any]:
    if not METRICS_PATH.is_file():
        raise FileNotFoundError(f"Metrics not found: {METRICS_PATH}")
    return json.loads(METRICS_PATH.read_text(encoding="utf-8"))
