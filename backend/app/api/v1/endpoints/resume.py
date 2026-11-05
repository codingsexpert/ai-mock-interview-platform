"""API routes for resume upload and parsing."""
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from backend.app.schemas.resume import ResumeParseResponse
from backend.app.services.pdf_parser import PDFParsingError, extract_text_from_pdf

router = APIRouter(prefix="/resume", tags=["Resume"])

# Maximum allowed resume size (10 MB)
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024


@router.post(
    "/parse",
    response_model=ResumeParseResponse,
    status_code=status.HTTP_200_OK,
    summary="Parse PDF Resume",
    description="Extracts plain text and document metrics from an uploaded PDF resume.",
)
async def parse_resume(file: UploadFile = File(...)):
    """Upload and extract text from a PDF resume."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF files are supported.",
        )

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds maximum threshold of 10MB.",
        )

    try:
        parsed_result = extract_text_from_pdf(
            file_bytes=file_bytes,
            filename=file.filename,
        )
        return parsed_result
    except PDFParsingError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error
