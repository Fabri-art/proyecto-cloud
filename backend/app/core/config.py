from __future__ import annotations

from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables / .env file.
    All values can be overridden via environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Application ──────────────────────────────────────────────────────────
    app_name: str = "Nombre-Creativo API"
    app_version: str = "0.1.0"
    debug: bool = False

    # ── Database ─────────────────────────────────────────────────────────────
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/nombre_creativo_db"
    )

    # ── Security ─────────────────────────────────────────────────────────────
    secret_key: str = "change-me"

    # ── CORS ─────────────────────────────────────────────────────────────────
    cors_origins: Union[str, List[str]] = [
        "http://localhost:5173",   # Svelte dev
        "http://localhost:4173",   # Svelte preview
    ]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v


# Singleton instance – import this throughout the app
settings = Settings()
