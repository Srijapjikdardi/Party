"""
Shared FastAPI dependencies for the API layer (auth extraction, etc.).
"""
from typing import Optional
from uuid import UUID

from fastapi import Depends, Header, Request
from sqlmodel import Session

from app.core.errors import AppError
from app.core.security import InvalidTokenError, decode_access_token
from app.db.session import get_session
from app.models import User
from app.repositories import UserRepository


def get_client_ip(request: Request) -> Optional[str]:
    return request.client.host if request.client else None


def get_current_user(
    authorization: Optional[str] = Header(None),
    session: Session = Depends(get_session),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise AppError(401, "not_authenticated", "Not authenticated")
    token = authorization.split(" ", 1)[1]

    try:
        payload = decode_access_token(token)
    except InvalidTokenError as exc:
        raise AppError(401, "invalid_token", str(exc)) from exc

    try:
        user_id = UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise AppError(401, "invalid_token", "Malformed token subject") from exc

    user = UserRepository(session).get(user_id)
    if not user or not user.is_active or user.deleted_at is not None:
        raise AppError(401, "invalid_token", "User not found or inactive")
    return user


def get_optional_user(
    authorization: Optional[str] = Header(None),
    session: Session = Depends(get_session),
) -> Optional[User]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        return get_current_user(authorization, session)
    except AppError:
        return None
