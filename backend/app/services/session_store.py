"""Session state management service."""
from typing import Dict, Optional
import uuid
from backend.app.graph.state import InterviewState


class SessionStore:
    """In-memory session registry with thread-safe access patterns."""

    def __init__(self):
        self._sessions: Dict[str, InterviewState] = {}

    def create_session(
        self,
        resume_text: str,
        job_description: str,
        target_role: str,
        max_turns: int = 5,
        focus_areas: Optional[list] = None,
        question_syllabus: Optional[list] = None,
    ) -> InterviewState:
        """Initialize and persist a new interview session state."""
        session_id = str(uuid.uuid4())
        initial_state: InterviewState = {
            "session_id": session_id,
            "target_role": target_role,
            "resume_text": resume_text,
            "job_description": job_description,
            "max_turns": max_turns,
            "current_turn": 0,
            "current_phase": "introduction",
            "focus_areas": focus_areas or ["Core Technical Competencies", "System Architecture"],
            "candidate_strengths": [],
            "question_syllabus": question_syllabus or [],
            "messages": [],
            "evaluations": [],
            "final_scorecard": None,
        }
        self._sessions[session_id] = initial_state
        return initial_state

    def get_session(self, session_id: str) -> Optional[InterviewState]:
        """Retrieve active session state by ID."""
        return self._sessions.get(session_id)

    def update_session(self, session_id: str, state: InterviewState) -> None:
        """Update active session state."""
        self._sessions[session_id] = state

    def session_exists(self, session_id: str) -> bool:
        """Check if session exists."""
        return session_id in self._sessions


# Global singleton instance
session_store = SessionStore()
