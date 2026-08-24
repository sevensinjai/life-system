"""Application settings, loaded from the environment."""

from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# 32+ bytes, matching the minimum RFC 7518 recommends for HMAC-SHA256.
DEV_JWT_SECRET = "dev-only-insecure-secret-change-me-before-deploying"
MIN_JWT_SECRET_BYTES = 32


class Settings(BaseSettings):
    """Settings read from environment variables or a local .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        extra="ignore",
    )

    app_name: str = "system-api"
    environment: Literal["development", "test", "production"] = "development"
    debug: bool = False
    version: str = "0.1.0"

    host: str = "127.0.0.1"
    port: int = 8000

    cors_origins: list[str] = ["*"]

    # The browser test client served at /web. Off is a reasonable choice for a
    # production deployment whose only client is the app.
    web_client: bool = True

    database_url: str = "sqlite:///./system.db"

    jwt_secret: str = DEV_JWT_SECRET
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 14  # two weeks; it is a phone app

    # Progression tuning. Changing these reshapes the whole level curve, so they
    # live in settings rather than as literals buried in the service layer.
    exp_curve_base: int = 100
    exp_curve_exponent: float = 1.5
    stat_points_per_level: int = 3
    penalty_exp_multiplier: float = 1.0

    # How often a constellation agrees to hear a request to befriend it, and
    # how long you wait before asking again after it says no. Settings rather
    # than literals because this is the number most likely to want tuning once
    # real players meet it — and because a future arbiter that actually reads
    # the request will want the chance one to stay switchable.
    friendship_accept_rate: float = 0.30
    friendship_retry_days: int = 7

    @model_validator(mode="after")
    def _check_jwt_secret(self) -> "Settings":
        """Refuse to start production with a weak or default signing key."""
        if self.environment != "production":
            return self

        if self.jwt_secret == DEV_JWT_SECRET:
            raise ValueError(
                "APP_JWT_SECRET must be set to a real secret when "
                "APP_ENVIRONMENT=production. Generate one with: "
                "python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        if len(self.jwt_secret.encode()) < MIN_JWT_SECRET_BYTES:
            raise ValueError(
                f"APP_JWT_SECRET must be at least {MIN_JWT_SECRET_BYTES} bytes "
                "for HMAC-SHA256 (RFC 7518 section 3.2)."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    """Return the cached settings instance."""
    return Settings()
