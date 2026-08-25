"""Database engine, session factory, and the declarative base."""

from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """Declarative base for every ORM model."""


def enable_sqlite_foreign_keys(engine) -> None:
    """Turn on foreign key enforcement, which SQLite leaves off by default.

    Every foreign key in this schema carries an ondelete rule — CASCADE so a
    deleted player takes their quests, skills and quotes with them, SET NULL
    so a deleted skill leaves the quests that named it intact. Without this
    pragma SQLite ignores all of them and orphans survive. It has to be set
    per connection, hence the event listener rather than a one-off statement.
    """

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_engine_from_url(database_url: str):
    """Build an engine, applying the connect args SQLite needs.

    SQLite refuses cross-thread use by default, which breaks under a threaded
    ASGI server; other backends take the argument as-is.
    """
    connect_args = {}
    is_sqlite = database_url.startswith("sqlite")
    if is_sqlite:
        connect_args["check_same_thread"] = False

    engine = create_engine(database_url, connect_args=connect_args, future=True)
    if is_sqlite:
        enable_sqlite_foreign_keys(engine)
    return engine


engine = create_engine_from_url(get_settings().database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a session that always closes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
