"""Test suite for PDF assessment report generation endpoint."""
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_pdf_report_download():
    """Verify endpoint generates valid PDF binary stream for a session."""
    # 1. Start session
    start_payload = {
        "resume_text": "Sample resume content for report generation.",
        "job_description": "Sample job description requirements.",
        "target_role": "Backend Engineer",
        "max_turns": 3,
    }
    start_res = client.post("/api/v1/interview/start", json=start_payload)
    assert start_res.status_code == 200
    session_id = start_res.json()["session_id"]

    # 2. Add turn
    turn_payload = {
        "session_id": session_id,
        "user_answer": "I have experience with Python, FastAPI and building robust APIs.",
    }
    client.post("/api/v1/interview/turn", json=turn_payload)

    # 3. Request PDF report
    pdf_res = client.get(f"/api/v1/interview/session/{session_id}/report.pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 500
    assert pdf_res.content.startswith(b"%PDF")
