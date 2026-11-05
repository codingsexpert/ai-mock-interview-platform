"""Test suite for PDF resume parsing service and API endpoint."""
import io
from fastapi.testclient import TestClient
from pypdf import PageObject, PdfWriter
from backend.app.main import app

client = TestClient(app)


def _create_sample_pdf_bytes(text_content: str = "Mukesh Singh - Senior Software Engineer") -> bytes:
    """Helper to generate a lightweight in-memory PDF with text."""
    writer = PdfWriter()
    # Add a blank page with metadata
    page = PageObject.create_blank_page(width=612, height=792)
    writer.add_page(page)
    # Add text via annotation / content stream
    buffer = io.BytesIO()
    writer.write(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def test_reject_non_pdf_file():
    """Verify endpoint rejects files without .pdf extension."""
    files = {"file": ("resume.txt", b"plain text resume", "text/plain")}
    response = client.post("/api/v1/resume/parse", files=files)
    assert response.status_code == 400
    assert "Only PDF files are supported" in response.json()["detail"]


def test_reject_empty_pdf_file():
    """Verify endpoint rejects empty 0-byte PDF files."""
    files = {"file": ("empty.pdf", b"", "application/pdf")}
    response = client.post("/api/v1/resume/parse", files=files)
    assert response.status_code == 422
    assert "Uploaded file is empty" in response.json()["detail"]


def test_successful_pdf_text_extraction():
    """Verify valid PDF returns structured text and metrics."""
    # Build a standard PDF with readable text
    from pypdf import PdfWriter
    writer = PdfWriter()
    page = writer.add_blank_page(width=200, height=200)
    
    # We write a basic PDF with text using standard PDF operators
    buffer = io.BytesIO()
    # Write a minimal valid PDF containing text
    minimal_pdf = (
        b"%PDF-1.4\n"
        b"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
        b"2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
        b"3 0 obj <</Type /Page /Parent 2 0 R /Resources <</Font <</F1 4 0 R>>>> /MediaBox [0 0 612 792] /Contents 5 0 R>> endobj\n"
        b"4 0 obj <</Type /Font /Subtype /Type1 /BaseFont /Helvetica>> endobj\n"
        b"5 0 obj <</Length 68>> stream\n"
        b"BT /F1 12 Tf 100 700 Td (Mukesh Singh Senior Software Engineer FastAPI Python) Tj ET\n"
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
        b"442\n"
        b"%%EOF"
    )

    files = {"file": ("mukesh_resume.pdf", minimal_pdf, "application/pdf")}
    response = client.post("/api/v1/resume/parse", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "mukesh_resume.pdf"
    assert data["page_count"] == 1
    assert "Mukesh Singh" in data["extracted_text"]
    assert "FastAPI" in data["extracted_text"]
    assert data["word_count"] >= 5
    assert data["character_count"] > 10
