"""Database engine and session management supporting PostgreSQL and async SQLite."""
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

Base = declarative_base()

# Configure database URL (PostgreSQL if set, otherwise async SQLite)
DB_URL = settings.database_url
if not DB_URL:
    DB_URL = "sqlite+aiosqlite:///./mock_interview.db"
    logger.info("DATABASE_URL not set in environment. Defaulting to local async SQLite: %s", DB_URL)

engine = create_async_engine(
    DB_URL,
    echo=False,
    future=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database tables asynchronously."""
    # Ensure all models are imported so Base.metadata knows about them
    import backend.app.models.interview  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema initialized successfully.")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency provider for database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
