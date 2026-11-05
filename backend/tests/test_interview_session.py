"""Test suite for live interview session management and conversational turns."""
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

SAMPLE_RESUME = (
    "Senior Python Developer with 4 years building APIs using FastAPI, PostgreSQL, and Redis. "
    "Designed asynchronous background workers using Celery and optimized database queries."
)
SAMPLE_JD = (
    "Looking for a Backend Engineer with strong Python and database optimization skills. "
    "Experience with microservices, Redis, and high availability systems required."
)


def test_start_session_lifecycle():
    """Verify session initialization and first question generation."""
    payload = {
        "resume_text": SAMPLE_RESUME,
        "job_description": SAMPLE_JD,
        "target_role": "Backend Engineer",
        "max_turns": 3,
    }
    response = client.post("/api/v1/interview/start", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["target_role"] == "Backend Engineer"
    assert data["current_phase"] == "introduction"
    assert data["max_turns"] == 3
    assert len(data["first_question"]) > 10


def test_full_conversational_turn_progression():
    """Verify answer submission, turn progression, shadow evaluation, and completion."""
    # 1. Start session
    start_payload = {
        "resume_text": SAMPLE_RESUME,
        "job_description": SAMPLE_JD,
        "target_role": "Backend Engineer",
        "max_turns": 3,
    }
    start_res = client.post("/api/v1/interview/start", json=start_payload)
    assert start_res.status_code == 200
    session_id = start_res.json()["session_id"]

    # 2. Turn 1 Answer
    turn1_payload = {
        "session_id": session_id,
        "user_answer": (
            "I have been working on building scalable APIs with FastAPI and PostgreSQL. "
            "My primary project was an analytics engine aggregating clickstream data."
        ),
    }
    t1_res = client.post("/api/v1/interview/turn", json=turn1_payload)
    assert t1_res.status_code == 200
    t1_data = t1_res.json()
    assert t1_data["turn_index"] == 1
    assert t1_data["is_completed"] is False
    assert len(t1_data["interviewer_question"]) > 0

    # 3. Turn 2 Answer
    turn2_payload = {
        "session_id": session_id,
        "user_answer": "We introduced Redis caching with TTL and write-through cache strategy to reduce DB read locks.",
    }
    t2_res = client.post("/api/v1/interview/turn", json=turn2_payload)
    assert t2_res.status_code == 200
    t2_data = t2_res.json()
    assert t2_data["turn_index"] == 2
    assert t2_data["is_completed"] is False

    # 4. Turn 3 Answer (Final Turn)
    turn3_payload = {
        "session_id": session_id,
        "user_answer": "We implemented circuit breakers with exponential backoff and fallback responses.",
    }
    t3_res = client.post("/api/v1/interview/turn", json=turn3_payload)
    assert t3_res.status_code == 200
    t3_data = t3_res.json()
    assert t3_data["turn_index"] == 3
    assert t3_data["is_completed"] is True

    # 5. Fetch Session State
    session_res = client.get(f"/api/v1/interview/session/{session_id}")
    assert session_res.status_code == 200
    state_data = session_res.json()
    assert len(state_data["evaluations"]) == 3
    # Verify evaluations contain proper criteria
    first_eval = state_data["evaluations"][0]
    assert "technical_accuracy_score" in first_eval
    assert "communication_clarity_score" in first_eval
    assert "key_strengths" in first_eval
    assert "critical_deficits" in first_eval


def test_invalid_session_returns_404():
    """Verify nonexistent session returns 404."""
    payload = {
        "session_id": "00000000-0000-0000-0000-000000000000",
        "user_answer": "sample answer",
    }
    response = client.post("/api/v1/interview/turn", json=payload)
    assert response.status_code == 404

