"""Password hashing and JSON Web Token handling."""

from datetime import UTC, datetime, timedelta
import hashlib
import hmac
import secrets

import jwt
from app.config import Settings

PBKDF2_ITERATIONS = 600_000
PBKDF2_ALGORITHM = "sha256"


def hash_password(plain_password: str) -> str:
    """Hash a password with a Workers-compatible stdlib KDF."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        PBKDF2_ALGORITHM,
        plain_password.encode(),
        salt,
        PBKDF2_ITERATIONS,
    )
    return f"pbkdf2_{PBKDF2_ALGORITHM}${PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a password against its stored hash."""
    try:
        scheme, iterations, salt_hex, expected_hex = hashed_password.split("$", 3)
        if scheme != f"pbkdf2_{PBKDF2_ALGORITHM}":
            return False
        actual = hashlib.pbkdf2_hmac(
            PBKDF2_ALGORITHM,
            plain_password.encode(),
            bytes.fromhex(salt_hex),
            int(iterations),
        )
        return hmac.compare_digest(actual, bytes.fromhex(expected_hex))
    except (TypeError, ValueError):
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
