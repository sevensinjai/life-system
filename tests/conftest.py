"""Test fixtures: an isolated in-memory database and an authenticated client."""

from collections.abc import Generator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings
from app.db import Base, enable_sqlite_foreign_keys, get_db
from app.main import create_app

# Importing the models package registers every table on Base.metadata.
import app.models  # noqa: F401


@pytest.fixture
def settings() -> Settings:
    return Settings(
        environment="test",
        app_name="system-api",
        version="0.1.0",
        jwt_secret="test-secret-that-is-long-enough-for-hs256",
        database_url="sqlite://",
    )


@pytest.fixture
def db_engine():
    """A fresh in-memory database per test.

    StaticPool keeps every connection pointed at the same in-memory database;
    without it each connection would get its own empty one.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    # Match the application engine, so ondelete rules behave the same in tests.
    enable_sqlite_foreign_keys(engine)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def session_factory(db_engine):
    return sessionmaker(bind=db_engine, autoflush=False, expire_on_commit=False)


@pytest.fixture
def db(session_factory) -> Generator[Session, None, None]:
    """A session for tests that drive the service layer directly."""
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(settings, session_factory) -> Generator[TestClient, None, None]:
    app = create_app(settings)

    def override_get_db() -> Generator[Session, None, None]:
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


REGISTRATION = {
    "email": "hunter@example.com",
    "password": "shadow-monarch-1",
    "name": "Sung Jinwoo",
    "timezone": "Asia/Seoul",
}


@pytest.fixture
def auth_client(client: TestClient) -> TestClient:
    """A client with a registered player's bearer token already attached."""
    response = client.post("/auth/register", json=REGISTRATION)
    assert response.status_code == 201, response.text
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.fixture
def player(auth_client, db):
    """The registered player, loaded through a direct session."""
    from app.models import Player

    return db.query(Player).one()


def at(year: int, month: int, day: int, hour: int = 12) -> datetime:
    """A fixed UTC instant, for tests that need a controlled clock."""
    return datetime(year, month, day, hour, tzinfo=UTC)


def befriend(db, player, constellation, *, when: datetime | None = None):
    """Put a player and a constellation on friendly terms directly.

    The real way in is to ask and clear the trial of admission, which
    tests/test_friendship.py covers end to end. Everything else only needs the
    channel open, so it shortcuts to the state that opens it.
    """
    from app.services.constellations import ensure_favor

    favor = ensure_favor(db, player, constellation)
    favor.is_friend = True
    favor.befriended_at = when or datetime(2026, 8, 24, 12, tzinfo=UTC)
    db.flush()
    return favor
