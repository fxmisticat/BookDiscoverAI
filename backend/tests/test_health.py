from fastapi.testclient import TestClient

from app.main import app


def test_healthz() -> None:
    client = TestClient(app)
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_settings_roundtrip() -> None:
    client = TestClient(app)
    payload = {"abs_url": "http://localhost:1337", "demo_mode": False}
    response = client.post("/api/settings", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["abs_url"] == payload["abs_url"]
    assert body["demo_mode"] is False

    response = client.get("/api/settings")
    assert response.status_code == 200
    assert response.json()["abs_url"] == payload["abs_url"]


def test_recommendations() -> None:
    client = TestClient(app)
    response = client.get("/api/recommendations?limit=3")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert len(body["items"]) == 3
    assert all("book" in item for item in body["items"])


def test_trope_feed() -> None:
    client = TestClient(app)
    trigger = client.post("/api/tropes/extract")
    assert trigger.status_code == 200
    feed = client.get("/api/discovery/trope-feed?limit=3")
    assert feed.status_code == 200
    body = feed.json()
    assert "items" in body
    assert len(body["items"]) >= 1
    first = body["items"][0]
    assert "matched_tropes" in first
    assert "explanation" in first
