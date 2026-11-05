"""Test suite for voice synthesis service and endpoint."""
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_reject_empty_synthesis_request():
    """Verify endpoint rejects empty string for synthesis."""
    payload = {"text": ""}
    response = client.post("/api/v1/voice/synthesize", json=payload)
    assert response.status_code == 422


def test_successful_speech_synthesis():
    """Verify endpoint generates valid non-empty audio stream."""
    payload = {"text": "Welcome to the technical interview."}
    response = client.post("/api/v1/voice/synthesize", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
    assert len(response.content) > 100
