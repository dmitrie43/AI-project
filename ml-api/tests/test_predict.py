from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.ml.model_store import load_model

client = TestClient(app)


def setup_module() -> None:
    load_model()


def test_metrics() -> None:
    r = client.get("/metrics")
    assert r.status_code == 200
    body = r.json()
    assert "baseline_majority" in body
    assert "model_logistic" in body


def test_predict_openish_ticket() -> None:
    r = client.post(
        "/predict",
        json={
            "category": "vpn",
            "priority": 5,
            "satisfaction": None,
            "tag_count": 2,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["prediction"] in (0, 1)
    assert "probabilities" in body
    assert set(body["features_used"]) == {
        "category",
        "priority",
        "satisfaction",
        "tag_count",
    }


def test_predict_requires_category() -> None:
    r = client.post("/predict", json={"priority": 2})
    assert r.status_code == 422
