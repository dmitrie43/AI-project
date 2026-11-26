"""Pydantic request/response models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    category: str = Field(..., examples=["vpn"])
    priority: float | None = Field(default=None, examples=[4])
    satisfaction: float | None = Field(default=None, examples=[3])
    tag_count: float | None = Field(default=0, examples=[2])


class PredictResponse(BaseModel):
    prediction: int
    label: str
    probabilities: dict[str, float]
    features_used: list[str]


class MetricsResponse(BaseModel):
    metrics: dict[str, Any]
