"""Pydantic schemas for interview orchestration and gap analysis."""
from typing import List, Optional
from pydantic import BaseModel, Field


class GapAnalysis(BaseModel):
    """Detailed comparison between resume competencies and job requirements."""

    matched_skills: List[str] = Field(default_factory=list, description="Skills verified in both resume and JD")
    missing_or_weak_skills: List[str] = Field(default_factory=list, description="Critical JD requirements absent or brief in resume")
    primary_risks: List[str] = Field(default_factory=list, description="Key technical areas to probe aggressively")


class InterviewPlanRequest(BaseModel):
    """Payload to initiate interview planning and gap analysis."""

    resume_text: str = Field(..., min_length=20, description="Sanitized plain text extracted from resume")
    job_description: str = Field(..., min_length=10, description="Target job description requirements")
    target_role: Optional[str] = Field(default="Software Engineer", description="Target role title")
    max_turns: Optional[int] = Field(default=5, ge=3, le=10, description="Total question turns for interview")


class InterviewPlanResponse(BaseModel):
    """Structured interview roadmap and question syllabus."""

    target_role: str = Field(..., description="Target role title")
    focus_areas: List[str] = Field(..., description="Core architectural and technical domains to evaluate")
    candidate_strengths: List[str] = Field(..., description="High-confidence skills identified in resume")
    gap_analysis: GapAnalysis = Field(..., description="Gap breakdown against JD")
    question_syllabus: List[str] = Field(..., description="5 progressive interview stage objectives")
