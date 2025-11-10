from functools import lru_cache
from typing import List

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    database_url: str = Field(
        default="sqlite:///./bookdiscover.db",
        description="SQLAlchemy-compatible database URL.",
    )
    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"],
        description="Allowed CORS origins for the frontend application.",
    )
    demo_mode: bool = Field(
        default=True,
        description="When enabled, the backend will operate with seed/demo data instead of external integrations.",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()
