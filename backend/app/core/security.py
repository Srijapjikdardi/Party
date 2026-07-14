"""
Password hashing, JWT access tokens, and opaque refresh-token helpers.

Access tokens are stateless signed JWTs (short-lived — no revocation
list needed, they just expire). Refresh tokens are opaque random
strings whose SHA-256 hash is stored in the `refresh_tokens` table
(app/models/refresh_token.py) — never the raw value. This split exists
because a JWT can't be truly revoked without maintaining a blocklist
(which then makes it no longer stateless, defeating the point), while
a DB-backed opaque token can be revoked/rotated/audited directly. See
docs/AUTHENTICATION.md.
"""
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.core.config import settings

ACCESS_TOKEN_TYPE = "access"


# ── Passwords ────────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=settings.bcrypt_rounds)).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        # Malformed/legacy hash (e.g. a pre-bcrypt SHA-256 hash from
        # before this milestone) — treat as a failed verification, not
        # a crash.
        return False


# ── Access tokens (JWT) ─────────────────────────────────

def create_access_token(user_id: uuid.UUID, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "role": role,
        "type": ACCESS_TOKEN_TYPE,
        "jti": uuid.uuid4().hex,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_ttl_minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


class InvalidTokenError(Exception):
    """Raised for any access-token decode/validation failure."""


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError as exc:
        raise InvalidTokenError("Access token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise InvalidTokenError("Invalid access token") from exc
    if payload.get("type") != ACCESS_TOKEN_TYPE:
        raise InvalidTokenError("Wrong token type")
    return payload


# ── Refresh tokens (opaque, DB-backed) ──────────────────

def generate_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def hash_token(raw_token: str) -> str:
    """Shared by refresh tokens, email-verification tokens, and
    password-reset tokens — all are opaque secrets hashed the same way
    before storage."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
