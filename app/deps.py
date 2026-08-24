"""Shared FastAPI dependencies: settings, database session, current player."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db import get_db
from app.errors import AuthenticationError
from app.models import Player, User
from app.security import decode_access_token

# auto_error=False so a missing header raises our JSON envelope, not Starlette's.
bearer_scheme = HTTPBearer(auto_error=False)

SettingsDep = Annotated[Settings, Depends(get_settings)]
DbDep = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DbDep,
    settings: SettingsDep,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ] = None,
) -> User:
    """Resolve the bearer token to a user, or raise 401."""
    if credentials is None or not credentials.credentials:
        raise AuthenticationError("Authorization header is missing.")

    subject = decode_access_token(credentials.credentials, settings)
    if subject is None:
        raise AuthenticationError("Token is invalid or has expired.")

    try:
        user_id = int(subject)
    except ValueError:
        raise AuthenticationError("Token subject is malformed.") from None

    user = db.get(User, user_id)
    if user is None:
        # The account was deleted while the token was still within its lifetime.
        raise AuthenticationError("Account no longer exists.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_player(db: DbDep, user: CurrentUser) -> Player:
    """The player profile attached to the authenticated user."""
    player = db.scalar(select(Player).where(Player.user_id == user.id))
    if player is None:
        raise AuthenticationError("No player profile exists for this account.")
    return player


CurrentPlayer = Annotated[Player, Depends(get_current_player)]
