"""Deployment-surface contract (not a substitute for real Vercel runtime verification)."""
from fastapi.testclient import TestClient
from app import app

def test_vercel_entrypoint_routes_to_same_backend():
    client=TestClient(app)
    response=client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "TEST_ONLY"
    root=client.get("/")
    assert root.status_code == 200
    assert "UALP" in root.text

def test_private_api_fails_closed_without_env(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("UALP_ACCESS_KEY", raising=False)
    client=TestClient(app)
    response=client.get("/api/forms/UALP_WV21_RU_LIKERT")
    assert response.status_code == 503
