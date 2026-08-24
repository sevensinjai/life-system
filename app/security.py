"""Password hashing and JSON Web Token handling."""

from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.config import Settings

_password_hash = PasswordHash.recommended()


def hash_password(plain_password: str) -> str:
    """Hash a password for storage (Argon2)."""
    return _password_hash.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a password against its stored hash."""
    try:
        return _password_hash.verify(plain_password, hashed_password)
    except Exception:
        # A malformed or truncated hash must read as a failed login, not a 500.
        return False


def create_access_token(subject: str, settings: Settings) -> str:
    """Mint a signed access token for the given user id."""
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, settings: Settings) -> str | None:
    """Return the subject of a valid token, or None if it is invalid or expired."""
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except jwt.PyJWTError:
        return None
    subject = payload.get("sub")
    return subject if isinstance(subject, str) else None
