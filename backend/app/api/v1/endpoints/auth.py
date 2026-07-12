from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlmodel import Session

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import User
from app.schemas import UserCreate, UserLogin, UserRead
from app.services import AuthError, AuthService

router = APIRouter(tags=["auth"])


@router.post("/auth/signup")
def signup(user_data: UserCreate, session: Session = Depends(get_session)):
    try:
        token, user = AuthService(session).signup(user_data)
    except AuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"token": token, "user": UserRead.model_validate(user)}


@router.post("/auth/signin")
def signin(creds: UserLogin, session: Session = Depends(get_session)):
    try:
        token, user = AuthService(session).signin(creds)
    except AuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return {"token": token, "user": UserRead.model_validate(user)}


@router.post("/auth/signout")
def signout(authorization: Optional[str] = Header(None), session: Session = Depends(get_session)):
    if authorization and authorization.startswith("Bearer "):
        AuthService(session).signout(authorization.split(" ", 1)[1])
    return {"message": "Signed out"}


@router.get("/users/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user
