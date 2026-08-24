"""Application settings, loaded from the environment."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings read from environment variables or a local .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        extra="ignore",
    )

    app_name: str = "cat-only-svg-api"
    environment: Literal["development", "test", "production"] = "development"
    debug: bool = False
    version: str = "0.1.0"

    host: str = "127.0.0.1"
    port: int = 8000

    # Comma-separated in the environment, e.g. APP_CORS_ORIGINS='["http://localhost:5173"]'
    cors_origins: list[str] = ["*"]


@lru_cache
def get_settings() -> Settings:
    """Return the cached settings instance."""
    return Settings()
