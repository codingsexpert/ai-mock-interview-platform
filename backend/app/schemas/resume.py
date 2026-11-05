"""Pydantic schemas for resume processing."""
from pydantic import BaseModel, Field


class ResumeParseResponse(BaseModel):
    """Structured response model for parsed resume content."""

    filename: str = Field(..., description="Uploaded resume file name")
    page_count: int = Field(..., ge=1, description="Total pages extracted from PDF")
    word_count: int = Field(..., ge=0, description="Total word count of extracted text")
    character_count: int = Field(..., ge=0, description="Total characters extracted")
    extracted_text: str = Field(..., min_length=1, description="Sanitized plain text extracted from PDF")

