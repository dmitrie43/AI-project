"""
ML API entrypoint.

  GET  /health
  GET  /metrics
  POST /analyze  (multipart field: `file`)
  POST /predict  (JSON ticket features)
"""

from __future__ import annotations

import io
import logging
from contextlib import asynccontextmanager
from typing import Any

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.ml.model_store import load_model, predict_one, read_metrics
from app.schemas import PredictRequest, PredictResponse

logger = logging.getLogger("ml-api")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        load_model()
        logger.info("Model artifact loaded")
    except FileNotFoundError as exc:
        logger.warning("%s", exc)
    yield


app = FastAPI(
    title="Internal Assistant ML API",
    version="0.1.0",
    description="Analytics and ML sidecar for Internal Assistant",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ml-api"}


@app.get("/metrics")
def metrics() -> dict[str, Any]:
    """Return last training report (baseline + model scores)."""
    try:
        return read_metrics()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/predict", response_model=PredictResponse)
def predict(body: PredictRequest) -> PredictResponse:
    """
    Infer is_open for one ticket from features known at prediction time.
    """
    try:
        result = predict_one(body.model_dump())
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Predict failed: {exc}") from exc

    return PredictResponse(**result)


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)) -> dict[str, Any]:
    """
    Upload CSV → simple aggregates JSON.

    Utility endpoint (not used for model training).
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload a .csv file")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        df = pd.read_csv(io.BytesIO(raw))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Cannot parse CSV: {exc}") from exc

    if df.empty:
        raise HTTPException(status_code=400, detail="CSV has no rows")

    numeric = df.select_dtypes(include="number")
    describe: dict[str, Any] = {}
    if not numeric.empty:
        describe = numeric.describe().round(4).to_dict()

    return {
        "filename": file.filename,
        "rows": int(len(df)),
        "columns": list(df.columns.astype(str)),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "null_counts": {col: int(df[col].isna().sum()) for col in df.columns},
        "numeric_describe": describe,
    }
