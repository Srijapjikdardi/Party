"""
Simple token-based auth.
In production, replace with JWT (python-jose) or OAuth.
"""
import hashlib
import secrets
from datetime import datetime, timedelta

# In-memory token store: {token: {"user_id": int, "expires": datetime}}
_token_store: dict = {}

def hash_password(password: str) -> str:
    """Simple SHA-256 hash. Use bcrypt in production."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed

def create_token(user_id: int) -> str:
    token = secrets.token_hex(32)
    _token_store[token] = {
        "user_id": user_id,
        "expires": datetime.utcnow() + timedelta(days=30)
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

def revoke_token(token: str):
    _token_store.pop(token, None)
