"""
Shared FastAPI dependencies for the API layer (auth extraction, etc.).
"""
from typing import Optional

from fastapi import Depends, Header, HTTPException
from sqlmodel import Session

from app.core.security import get_user_id_from_token
from app.db.session import get_session
from app.models import User
from app.repositories import UserRepository


def get_current_user(
    authorization: Optional[str] = Header(None),
    session: Session = Depends(get_session),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    user_id = get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = UserRepository(session).get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_optional_user(
    authorization: Optional[str] = Header(None),
    session: Session = Depends(get_session),
) -> Optional[User]:
    try:
        return get_current_user(authorization, session)
    except HTTPException:
        return None
