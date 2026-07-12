"""
Database engine and session management.
"""
from typing import Iterator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

# check_same_thread=False is required for SQLite when accessed from FastAPI's
# threaded request handling; harmless for other database engines.
_connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    connect_args=_connect_args,
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """FastAPI dependency that yields a DB session per request."""
    with Session(engine) as session:
        yield session
