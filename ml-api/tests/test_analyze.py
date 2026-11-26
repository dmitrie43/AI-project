from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_analyze_csv() -> None:
    csv_bytes = b"category,priority\nvpn,3\naccess,2\nvpn,1\n"
    r = client.post(
        "/analyze",
        files={"file": ("tickets.csv", csv_bytes, "text/csv")},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["rows"] == 3
    assert "category" in body["columns"]
    assert body["null_counts"]["category"] == 0


def test_analyze_rejects_non_csv() -> None:
    r = client.post(
        "/analyze",
        files={"file": ("note.txt", b"hello", "text/plain")},
    )
    assert r.status_code == 400
