"""Pydantic schemas for live interview session management and conversational turns."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SessionStartRequest(BaseModel):
    """Payload to launch a new interview session."""

    resume_text: str = Field(..., min_length=20, description="Sanitized plain text extracted from resume")
    job_description: str = Field(..., min_length=10, description="Target job requirements")
    target_role: Optional[str] = Field(default="Software Engineer", description="Target role title")
    max_turns: Optional[int] = Field(default=5, ge=3, le=10, description="Total interview question turns")


class SessionStartResponse(BaseModel):
    """Initial session response containing session ID and opening question."""

    session_id: str = Field(..., description="Unique UUID for interview session")
    target_role: str = Field(..., description="Target role title")
    first_question: str = Field(..., description="Opening calibration question from interviewer")
    current_phase: str = Field(..., description="Current interview phase")
    max_turns: int = Field(..., description="Total planned question turns")


class TurnRequest(BaseModel):
    """Payload when candidate submits an answer to the current question."""

    session_id: str = Field(..., description="Active session ID")
    user_answer: str = Field(..., min_length=1, description="Candidate verbal or text response")


class TurnResponse(BaseModel):
    """Response containing interviewer's subsequent question or completion signal."""

    session_id: str = Field(..., description="Active session ID")
    turn_index: int = Field(..., description="Current turn number completed")
    current_phase: str = Field(..., description="Current interview phase")
    interviewer_question: str = Field(..., description="Next question or closing statement")
    is_completed: bool = Field(..., description="True if interview session has concluded")

