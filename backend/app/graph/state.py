"""LangGraph state schema for interview lifecycle management."""
from typing import Any, Dict, List, Literal, Optional, TypedDict


class InterviewMessage(TypedDict):
    """Single conversational turn entry."""
    role: Literal["assistant", "user", "system"]
    content: str
    timestamp: str


class TurnEvaluation(TypedDict):
    """Silent evaluation record for a single answer turn."""
    turn_index: int
    question: str
    candidate_answer: str
    technical_accuracy_score: float
    communication_clarity_score: float
    key_strengths: List[str]
    critical_deficits: List[str]
    suggested_ideal_response: str


class InterviewState(TypedDict):
    """Global state container for LangGraph interview workflow."""
    session_id: str
    target_role: str
    resume_text: str
    job_description: str
    max_turns: int
    current_turn: int
    current_phase: Literal[
        "planning",
        "introduction",
        "project_deepdive",
        "technical_core",
        "situational_architecture",
        "conclusion",
        "completed",
    ]
    focus_areas: List[str]
    candidate_strengths: List[str]
    question_syllabus: List[str]
    messages: List[InterviewMessage]
    evaluations: List[TurnEvaluation]
    final_scorecard: Optional[Dict[str, Any]]

