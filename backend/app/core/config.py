"""
Centralized application configuration.

All configuration is sourced from environment variables (with sensible
local-development defaults), following the 12-factor app pattern. Set
values via a `.env` file at the repo root (see `.env.example`) or real
environment variables in production. Nothing environment-specific
should be hardcoded anywhere else in the codebase — import `settings`
from here instead.
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py -> backend/app/core -> backend/app -> backend -> repo root
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────
    app_name: str = "PartyPe API"
    app_version: str = "2.0"
    environment: str = "development"  # development | staging | production
    debug: bool = True

    # ── API versioning ───────────────────────────────────
    api_v1_prefix: str = "/api/v1"
    # Unversioned alias kept for the legacy static SPA (frontend/legacy-spa)
    # while the Next.js migration is in progress. Remove once that SPA is
    # retired — see docs/MIGRATION_PLAN.md.
    legacy_api_prefix: str = "/api"

    # ── Database ─────────────────────────────────────────
    database_url: str = f"sqlite:///{REPO_ROOT}/partype.db"
    database_echo: bool = False

    # ── CORS ─────────────────────────────────────────────
    # Comma-separated list of allowed origins, e.g. "http://localhost:3000,https://partype.com"
    cors_allow_origins: str = "*"

    # ── Auth ─────────────────────────────────────────────
    token_ttl_days: int = 30

    # ── Legacy static frontend ───────────────────────────
    frontend_dir: Path = REPO_ROOT / "frontend" / "legacy-spa"

    @property
    def cors_origins_list(self) -> list[str]:
        if self.cors_allow_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor — env vars are read once per process."""
    return Settings()


settings = get_settings()
