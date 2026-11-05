"""Test suite for interview planning and gap analysis endpoint."""
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_interview_plan_validation_failure():
    """Verify endpoint rejects requests with excessively short text."""
    payload = {
        "resume_text": "too short",
        "job_description": "short",
        "target_role": "Backend Engineer",
    }
    response = client.post("/api/v1/interview/plan", json=payload)
    assert response.status_code == 422


def test_interview_plan_generation_success():
    """Verify endpoint generates structured 5-stage syllabus and gap analysis."""
    payload = {
        "resume_text": (
            "Senior Backend Engineer with 5 years experience in Python, FastAPI, and PostgreSQL. "
            "Designed high-throughput microservices handling 10k requests per second with Redis caching. "
            "Implemented CI/CD pipelines and Docker containerization."
        ),
        "job_description": (
            "Looking for a Senior Backend Developer proficient in Python, FastAPI, and PostgreSQL. "
            "Experience with Kubernetes, AWS, and distributed messaging (Kafka/RabbitMQ) is required."
        ),
        "target_role": "Senior Backend Engineer",
        "max_turns": 5,
    }

    response = client.post("/api/v1/interview/plan", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["target_role"] == "Senior Backend Engineer"
    assert len(data["focus_areas"]) > 0
    assert len(data["candidate_strengths"]) > 0

    gap = data["gap_analysis"]
    assert "matched_skills" in gap
    assert "missing_or_weak_skills" in gap
    assert "primary_risks" in gap

    # Verify syllabus structure has 5 stages
    assert len(data["question_syllabus"]) == 5
    assert any("Stage 1" in s for s in data["question_syllabus"])
    assert any("Stage 2" in s for s in data["question_syllabus"])
    assert any("Stage 5" in s for s in data["question_syllabus"])

