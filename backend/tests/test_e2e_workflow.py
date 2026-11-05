"""End-to-End automated testing suite simulating complete candidate journey."""
import io
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

MOCK_PDF_BYTES = (
    b"%PDF-1.4\n"
    b"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
    b"2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
    b"3 0 obj <</Type /Page /Parent 2 0 R /Resources <</Font <</F1 4 0 R>>>> /MediaBox [0 0 612 792] /Contents 5 0 R>> endobj\n"
    b"4 0 obj <</Type /Font /Subtype /Type1 /BaseFont /Helvetica>> endobj\n"
    b"5 0 obj <</Length 145>> stream\n"
    b"BT /F1 12 Tf 50 700 Td (Mukesh Singh Senior Backend Engineer FastAPI PostgreSQL Redis Docker Kubernetes Microservices Kafka) Tj ET\n"
    b"endstream\n"
    b"endobj\n"
    b"xref\n"
    b"0 6\n"
    b"0000000000 65535 f \n"
    b"0000000010 00000 n \n"
    b"0000000060 00000 n \n"
    b"0000000117 00000 n \n"
    b"0000000244 00000 n \n"
    b"0000000323 00000 n \n"
    b"trailer <</Size 6 /Root 1 0 R>>\n"
    b"startxref\n"
    b"519\n"
    b"%%EOF"
)

JOB_DESCRIPTION = (
    "Looking for a Senior Backend Developer proficient in Python, FastAPI, and PostgreSQL. "
    "Experience with microservices, Redis caching, and high-throughput distributed systems required."
)


def test_full_candidate_lifecycle_simulation():
    """Simulate complete lifecycle: parse resume -> plan interview -> start session -> complete 5 turns -> audit report."""
    # 1. Parse Resume
    files = {"file": ("mukesh_resume.pdf", MOCK_PDF_BYTES, "application/pdf")}
    parse_res = client.post("/api/v1/resume/parse", files=files)
    assert parse_res.status_code == 200
    resume_data = parse_res.json()
    assert "FastAPI" in resume_data["extracted_text"]
    assert resume_data["word_count"] > 5

    # 2. Generate Plan & Gap Analysis
    plan_payload = {
        "resume_text": resume_data["extracted_text"],
        "job_description": JOB_DESCRIPTION,
        "target_role": "Senior Backend Engineer",
        "max_turns": 5,
    }
    plan_res = client.post("/api/v1/interview/plan", json=plan_payload)
    assert plan_res.status_code == 200
    plan_data = plan_res.json()
    assert len(plan_data["question_syllabus"]) == 5
    assert len(plan_data["focus_areas"]) > 0

    # 3. Start Session
    start_payload = {
        "resume_text": resume_data["extracted_text"],
        "job_description": JOB_DESCRIPTION,
        "target_role": "Senior Backend Engineer",
        "max_turns": 5,
    }
    start_res = client.post("/api/v1/interview/start", json=start_payload)
    assert start_res.status_code == 200
    session_data = start_res.json()
    session_id = session_data["session_id"]
    assert session_data["current_phase"] == "introduction"

    # 4. Simulate 5 realistic conversational turns
    answers = [
        "I have 5 years experience building distributed backends with FastAPI and PostgreSQL, focusing on low latency APIs.",
        "In my recent project, we designed a high-throughput event processing pipeline handling 15,000 requests per second.",
        "To manage database load, we introduced Redis read-replicas, connection pooling with asyncpg, and composite indices.",
        "During cascading downstream failures, we implemented circuit breakers with exponential backoff and localized cache fallbacks.",
        "Looking back, I would have adopted event-driven architecture with Kafka earlier to decouple real-time write spikes.",
    ]

    for idx, answer in enumerate(answers, start=1):
        turn_payload = {"session_id": session_id, "user_answer": answer}
        turn_res = client.post("/api/v1/interview/turn", json=turn_payload)
        assert turn_res.status_code == 200
        turn_data = turn_res.json()
        assert turn_data["turn_index"] == idx
        if idx < 5:
            assert turn_data["is_completed"] is False
            assert len(turn_data["interviewer_question"]) > 10
        else:
            assert turn_data["is_completed"] is True

    # 5. Retrieve Final Session State & Verify Shadow Evaluations
    state_res = client.get(f"/api/v1/interview/session/{session_id}")
    assert state_res.status_code == 200
    final_state = state_res.json()

    assert len(final_state["evaluations"]) == 5
    # Verify each evaluation has scoring and model answers
    for ev in final_state["evaluations"]:
        assert ev["technical_accuracy_score"] >= 0.0
        assert ev["communication_clarity_score"] >= 0.0
        assert len(ev["key_strengths"]) > 0
        assert len(ev["critical_deficits"]) > 0
        assert len(ev["suggested_ideal_response"]) > 10

    # Total messages: 1 opening + 5 user answers + 5 assistant responses = 11 messages
    assert len(final_state["messages"]) == 11

