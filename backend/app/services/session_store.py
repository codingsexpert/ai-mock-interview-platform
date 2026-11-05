"""Session state management service with database persistence."""
import json
import logging
from typing import Dict, List, Optional
import uuid
from sqlalchemy import select
from backend.app.core.database import async_session_factory, init_db
from backend.app.graph.state import InterviewState
from backend.app.models.interview import InterviewSessionModel

logger = logging.getLogger(__name__)
_db_initialized = False


async def _ensure_db():
    global _db_initialized
    if not _db_initialized:
        await init_db()
        _db_initialized = True


class SessionStore:
    """Session registry managing memory caching and asynchronous database persistence."""

    def __init__(self):
        self._cache: Dict[str, InterviewState] = {}

    def create_session(
        self,
        resume_text: str,
        job_description: str,
        target_role: str,
        max_turns: int = 5,
        focus_areas: Optional[list] = None,
        question_syllabus: Optional[list] = None,
    ) -> InterviewState:
        """Initialize in-memory session state."""
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
        self._cache[session_id] = initial_state
        return initial_state

    def get_session(self, session_id: str) -> Optional[InterviewState]:
        """Retrieve active session state by ID."""
        return self._cache.get(session_id)

    def update_session(self, session_id: str, state: InterviewState) -> None:
        """Update active session cache."""
        self._cache[session_id] = state

    def session_exists(self, session_id: str) -> bool:
        """Check if session exists."""
        return session_id in self._cache

    async def persist_session_to_db(self, state: InterviewState) -> None:
        """Persist or update session record in the database."""
        await _ensure_db()
        session_id = state["session_id"]
        evals = state.get("evaluations", [])

        # Calculate live scores if evaluations exist
        comp_score, tech_score, comm_score = None, None, None
        if evals:
            avg_t = sum(e.get("technical_accuracy_score", 0.0) for e in evals) / len(evals)
            avg_c = sum(e.get("communication_clarity_score", 0.0) for e in evals) / len(evals)
            comp_score = round(((avg_t * 0.6) + (avg_c * 0.4)) * 10, 1)
            tech_score = round(avg_t, 1)
            comm_score = round(avg_c, 1)

        is_completed = state.get("current_turn", 0) >= state.get("max_turns", 5)

        try:
            async with async_session_factory() as db:
                stmt = select(InterviewSessionModel).where(InterviewSessionModel.session_id == session_id)
                result = await db.execute(stmt)
                record = result.scalar_one_or_none()

                serialized_state = json.dumps(state)

                if record is None:
                    new_record = InterviewSessionModel(
                        session_id=session_id,
                        target_role=state["target_role"],
                        total_turns=state["max_turns"],
                        completed_turns=state["current_turn"],
                        is_completed=is_completed,
                        composite_score=comp_score,
                        technical_score=tech_score,
                        communication_score=comm_score,
                        state_json=serialized_state,
                    )
                    db.add(new_record)
                else:
                    record.completed_turns = state["current_turn"]
                    record.is_completed = is_completed
                    record.composite_score = comp_score
                    record.technical_score = tech_score
                    record.communication_score = comm_score
                    record.state_json = serialized_state

                await db.commit()
        except Exception as exc:
            logger.error("Failed to persist session %s to database: %s", session_id, exc)

    async def get_history_from_db(self) -> List[Dict]:
        """Fetch all historical interview records ordered by creation date."""
        await _ensure_db()
        try:
            async with async_session_factory() as db:
                stmt = select(InterviewSessionModel).order_by(InterviewSessionModel.created_at.desc())
                result = await db.execute(stmt)
                records = result.scalars().all()
                return [
                    {
                        "session_id": r.session_id,
                        "target_role": r.target_role,
                        "total_turns": r.total_turns,
                        "completed_turns": r.completed_turns,
                        "is_completed": r.is_completed,
                        "composite_score": r.composite_score,
                        "technical_score": r.technical_score,
                        "communication_score": r.communication_score,
                        "created_at": r.created_at.isoformat() if r.created_at else None,
                    }
                    for r in records
                ]
        except Exception as exc:
            logger.error("Failed to fetch interview history: %s", exc)
            return []


# Global singleton instance
session_store = SessionStore()
