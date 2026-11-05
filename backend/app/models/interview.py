"""SQLAlchemy models for interview session persistence and historical scoring."""
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from backend.app.core.database import Base


class InterviewSessionModel(Base):
    """Database record of an interview session."""

    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), unique=True, index=True, nullable=False)
    target_role = Column(String(128), nullable=False)
    total_turns = Column(Integer, default=5, nullable=False)
    completed_turns = Column(Integer, default=0, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)

    composite_score = Column(Float, nullable=True)
    technical_score = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)

    state_json = Column(Text, nullable=False)  # Serialized InterviewState for full hydration

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
