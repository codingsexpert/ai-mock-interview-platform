"""Test suite for database persistence and historical interview retrieval."""
import asyncio
from fastapi.testclient import TestClient
from backend.app.core.database import init_db
from backend.app.main import app

client = TestClient(app)


def test_database_initialization():
    """Verify tables are created asynchronously without errors."""
    asyncio.run(init_db())


def test_session_persistence_and_history_retrieval():
    """Verify session is persisted to database and retrieved via GET /api/v1/interview/history."""
    # 1. Start a session
    payload = {
        "resume_text": "Experienced Python Engineer specializing in SQLAlchemy and FastAPI databases.",
        "job_description": "Seeking Python Backend Engineer with database schema modeling experience.",
        "target_role": "Database Architect",
        "max_turns": 3,
    }
    start_res = client.post("/api/v1/interview/start", json=payload)
    assert start_res.status_code == 200
    session_id = start_res.json()["session_id"]

    # 2. Complete a turn
    turn_res = client.post(
        "/api/v1/interview/turn",
        json={
            "session_id": session_id,
            "user_answer": "I have modeled schemas with PostgreSQL indexing, foreign keys, and partition pruning.",
        },
    )
    assert turn_res.status_code == 200

    # 3. Check history endpoint
    history_res = client.get("/api/v1/interview/history")
    assert history_res.status_code == 200
    history = history_res.json()
    assert isinstance(history, list)
    assert len(history) > 0

    # Match our created session
    matched = [h for h in history if h["session_id"] == session_id]
    assert len(matched) == 1
    session_record = matched[0]
    assert session_record["target_role"] == "Database Architect"
    assert session_record["completed_turns"] == 1
    assert session_record["composite_score"] is not None
