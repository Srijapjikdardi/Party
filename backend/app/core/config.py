"""
Centralized application configuration.

All configuration is sourced from environment variables (with sensible
local-development defaults), following the 12-factor app pattern. Set
values via a `.env` file at the repo root (see `.env.example`) or real
environment variables in production. Nothing environment-specific or
secret should be hardcoded anywhere else in the codebase — import
`settings` from here instead.
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
    app_version: str = "3.0"
    environment: str = "development"  # development | staging | production
    debug: bool = True

    # ── API versioning ───────────────────────────────────
    api_v1_prefix: str = "/api/v1"
    # Unversioned alias kept for the legacy static SPA (frontend/legacy-spa)
    # while the Next.js migration is in progress. Remove once that SPA is
    # retired — see docs/MIGRATION_PLAN.md.
    legacy_api_prefix: str = "/api"

    # ── Database (PostgreSQL / Neon) ─────────────────────
    # No default: a real Postgres URL is required. Get a free one from
    # https://neon.tech — see .env.example for the format Neon gives you.
    # Never hardcode credentials here; this only reads what's in .env /
    # the real environment.
    database_url: str
    database_echo: bool = False
    # Neon free tier: small compute, autosuspends the endpoint after
    # ~5 min idle, and each waking reconnect is comparatively slow — so
    # this pool favors "few, kept-alive, verified-before-use" over
    # "many, cheaply opened":
    #   pool_size: small — free tier's max_connections is limited and
    #     shared with Neon's own pooler; a large app-side pool just
    #     holds connections Neon has to account for.
    #   pool_pre_ping: issues a cheap SELECT 1 before handing out a
    #     pooled connection, so a connection Neon silently dropped
    #     during autosuspend/resume is transparently replaced instead
    #     of surfacing as a random query failure.
    #   pool_recycle: recycle connections older than this many seconds,
    #     comfortably under Neon's own idle-connection timeout, so the
    #     app never hands out a connection Neon already considers stale.
    db_pool_size: int = 5
    db_max_overflow: int = 5
    db_pool_recycle_seconds: int = 300
    db_pool_pre_ping: bool = True
    # Use Neon's pooled connection string (PgBouncer, port 6543 in
    # Neon's dashboard) for normal app traffic, not the direct endpoint
    # — see docs/DATABASE.md "Connection management".

    # ── CORS ─────────────────────────────────────────────
    # Comma-separated list of allowed origins, e.g. "http://localhost:3000,https://partype.com"
    cors_allow_origins: str = "*"

    # ── Auth ─────────────────────────────────────────────
    # JWT signing key for access tokens. No default — required, must be
    # a long random value from env/.env, never hardcoded or committed.
    # Generate one with: python -c "import secrets; print(secrets.token_urlsafe(64))"
    secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 15
    # Refresh tokens are opaque, DB-backed (app/models/refresh_token.py),
    # not JWTs — see docs/AUTHENTICATION.md for why.
    refresh_token_ttl_days: int = 30
    email_verification_ttl_hours: int = 24
    password_reset_ttl_minutes: int = 30
    bcrypt_rounds: int = 12
    # Brute-force protection (User.failed_login_attempts/locked_until,
    # not in-memory — see docs/AUTHENTICATION.md).
    max_failed_login_attempts: int = 5
    account_lockout_minutes: int = 15
    # Rate limiting (slowapi, in-memory backend — single-instance
    # limitation, acceptable on a free-tier single-dyno deployment; see
    # docs/AUTHENTICATION.md for the Redis upgrade path). Disabled in
    # tests via this flag so test suites aren't rate-limited by shared
    # state across test cases.
    rate_limit_enabled: bool = True
    google_client_id: str = ""
    apple_client_id: str = ""

    # ── Email (delivery is pluggable — see app/core/email.py) ────
    # Base URL used to build verification/password-reset links emailed
    # to users, e.g. "{public_app_url}/verify-email?token=...". No
    # frontend route exists at this URL yet — wiring it up is frontend
    # work, out of scope for this (backend) milestone.
    public_app_url: str = "http://localhost:3000"

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
