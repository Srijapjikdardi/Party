"""
Aggregates every v1 endpoint router into one. `app.main` mounts this
single router under both `/api/v1` (canonical) and `/api` (legacy
alias for the pre-Next.js SPA — see docs/MIGRATION_PLAN.md).
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, merchant, notifications, orders, restaurants, sessions, wallet

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(restaurants.router)
api_router.include_router(sessions.router)
api_router.include_router(orders.router)
api_router.include_router(wallet.router)
api_router.include_router(notifications.router)
api_router.include_router(merchant.router)
