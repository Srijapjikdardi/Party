"""
Token-based authentication primitives.

This is a simple in-memory bearer-token scheme, ported as-is from the
pre-restructure backend/auth.py. It is adequate for local development
and demos. For production, replace `hash_password` with bcrypt/argon2
and the in-memory `_token_store` with signed JWTs (python-jose) or a
persistent session store — tracked as a follow-up, not part of this
architecture milestone.
"""
import hashlib
import secrets
from datetime import datetime, timedelta

from app.core.config import settings

# In-memory token store: {token: {"user_id": int, "expires": datetime}}
_token_store: dict = {}


def hash_password(password: str) -> str:
    """Simple SHA-256 hash. Use bcrypt/argon2 in production."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed


def create_token(user_id: int) -> str:
    token = secrets.token_hex(32)
    _token_store[token] = {
        "user_id": user_id,
        "expires": datetime.utcnow() + timedelta(days=settings.token_ttl_days),
    }
    return token


def get_user_id_from_token(token: str) -> int | None:
    entry = _token_store.get(token)
    if not entry:
        return None
    if entry["expires"] < datetime.utcnow():
        del _token_store[token]
        return None
    return entry["user_id"]


def revoke_token(token: str) -> None:
    _token_store.pop(token, None)
