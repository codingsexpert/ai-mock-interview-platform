"""Test suite for health check endpoint."""
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_check_returns_200():
    """Verify GET /api/health responds with 200 and healthy status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app_name" in data
    assert "environment" in data
    assert data["version"] == "1.0.0"
