"""
Application factory. Wires together config, the versioned API router,
the legacy-compatibility alias, and the (temporary) static SPA mount.

Schema is owned by Alembic migrations (`alembic upgrade head`), not by
create-on-boot — startup no longer calls SQLModel.metadata.create_all().
Auto-creating tables from live model state bypasses migration history
and is exactly how schema drift between environments happens.
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlmodel import Session

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.rate_limit import limiter
from app.db.session import check_database_connection, engine
from app.seed import seed_if_empty


def create_app() -> FastAPI:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    app = FastAPI(title=settings.app_name, version=settings.app_version)

    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={"error": {"code": "rate_limited", "message": "Too many requests, please try again later"}},
        )

    @app.on_event("startup")
    def on_startup() -> None:
        # Dev convenience only — never runs against production data,
        # see app/seed.py's own guard. Requires `alembic upgrade head`
        # to have already been run; this does not create tables.
        if settings.environment == "development":
            with Session(engine) as session:
                seed_if_empty(session)

    @app.get("/health")
    def health_check():
        db_ok = check_database_connection()
        return {
            "status": "ok" if db_ok else "degraded",
            "app": settings.app_name,
            "environment": settings.environment,
            "database": "connected" if db_ok else "unreachable",
        }

    # Versioned API (canonical)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    # Unversioned alias for the legacy static SPA during the Next.js
    # migration (see docs/MIGRATION_PLAN.md). Remove once that SPA is retired.
    app.include_router(api_router, prefix=settings.legacy_api_prefix)

    # Legacy static SPA — served until the Next.js frontend replaces it.
    if settings.frontend_dir.exists():
        app.mount("/static", StaticFiles(directory=settings.frontend_dir), name="static")

        @app.get("/", response_class=HTMLResponse)
        async def read_root():
            index_path = settings.frontend_dir / "index.html"
            with open(index_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read(), status_code=200)

    return app


app = create_app()
