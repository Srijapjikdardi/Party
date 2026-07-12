# Development Guide

## Prerequisites

- Python 3.11+
- Node 20+ (scaffold built/verified against Node 22)

## Backend

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional — defaults work for local dev
python run.py
```

Runs at `http://localhost:8000`. `/docs` for Swagger UI, `/health` for a liveness check. First boot seeds demo data (see `backend/app/seed.py`) — demo accounts: `demo@partype.com` / `demo123`, `merchant@partype.com` / `merchant123`, `waiter@partype.com` / `waiter123`.

Legacy SPA is served at `/` for now (`frontend/legacy-spa/index.html`) — see `docs/MIGRATION_PLAN.md`.

Lint: `ruff check backend/app run.py`

## Frontend (Next.js — in progress, see docs/MIGRATION_PLAN.md)

```bash
cd frontend
npm install
npm run dev
```

Runs at `http://localhost:3000`, proxies `/api/v1/*` to the backend (must be running separately at `:8000`).

```bash
npm run typecheck   # tsc --noEmit
npm run lint          # next lint
npm run build         # production build
```

## Repository layout

```
backend/
  app/
    core/           settings + auth primitives
    db/             engine/session
    models/         SQLModel table models, one file per entity
    schemas/        Pydantic request/response models
    repositories/   DB access, one class per entity
    services/       business logic
    api/v1/         versioned FastAPI routers
    main.py         app factory
    seed.py         demo data
frontend/
  app/               Next.js App Router routes
  components/ui/     shadcn/ui primitives
  lib/                 API client, utils
  types/              TS types mirroring backend schemas
  legacy-spa/          pre-migration static SPA + design mockups
docs/                this directory
requirements.txt    Python deps (single source of truth)
.env.example         backend config template
run.py               dev entrypoint
```

See `docs/ARCHITECTURE.md` for the layer-by-layer breakdown and `docs/API.md` for the endpoint reference.
