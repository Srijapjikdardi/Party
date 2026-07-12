"""
Application factory. Wires together config, the versioned API router,
the legacy-compatibility alias, and the (temporary) static SPA mount.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.session import create_db_and_tables, engine
from app.seed import seed_if_empty


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version=settings.app_version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def on_startup() -> None:
        create_db_and_tables()
        with Session(engine) as session:
            seed_if_empty(session)

    @app.get("/health")
    def health_check():
        return {"status": "ok", "app": settings.app_name, "environment": settings.environment}

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
