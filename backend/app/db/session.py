"""
Database engine and session management.
"""
from typing import Iterator

from sqlalchemy import text
from sqlmodel import Session, create_engine

from app.core.config import settings

engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_recycle=settings.db_pool_recycle_seconds,
    pool_pre_ping=settings.db_pool_pre_ping,
)


def get_session() -> Iterator[Session]:
    """FastAPI dependency that yields a DB session per request."""
    with Session(engine) as session:
        yield session


def check_database_connection() -> bool:
    """Used by the /health endpoint. Cheap query, no schema dependency."""
    try:
        with Session(engine) as session:
            session.exec(text("SELECT 1"))
        return True
    except Exception:
        return False
