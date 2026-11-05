"""Service module for extracting and sanitizing text from PDF resumes."""
import io
import re
from pypdf import PdfReader
from backend.app.schemas.resume import ResumeParseResponse


class PDFParsingError(Exception):
    """Custom exception raised when PDF parsing fails."""
    pass


def extract_text_from_pdf(file_bytes: bytes, filename: str) -> ResumeParseResponse:
    """
    Extract sanitized plain text and metadata from raw PDF bytes.

    Args:
        file_bytes: In-memory raw bytes of uploaded PDF.
        filename: Name of the uploaded file.

    Returns:
        ResumeParseResponse with extracted text, page count, and word statistics.

    Raises:
        PDFParsingError: If file is corrupted, encrypted, or contains no readable text.
    """
    if not file_bytes:
        raise PDFParsingError("Uploaded file is empty.")

    try:
        pdf_stream = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_stream)

        if reader.is_encrypted:
            raise PDFParsingError("Password-protected PDFs are not supported.")

        total_pages = len(reader.pages)
        if total_pages == 0:
            raise PDFParsingError("PDF contains no readable pages.")

        page_texts = []
        for index, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            cleaned = text.strip()
            if cleaned:
                page_texts.append(cleaned)

        combined_text = "\n\n".join(page_texts)

        # Normalize redundant spaces and blank lines
        normalized_text = re.sub(r"[ \t]+", " ", combined_text)
        normalized_text = re.sub(r"\n{3,}", "\n\n", normalized_text).strip()

        if not normalized_text:
            raise PDFParsingError("No readable text found in PDF. Ensure document is not an image-only scan.")

        word_count = len(normalized_text.split())
        char_count = len(normalized_text)

        return ResumeParseResponse(
            filename=filename,
            page_count=total_pages,
            word_count=word_count,
            character_count=char_count,
            extracted_text=normalized_text,
        )

    except PDFParsingError:
        raise
    except Exception as exc:
        raise PDFParsingError(f"Failed to process PDF: {str(exc)}") from exc

