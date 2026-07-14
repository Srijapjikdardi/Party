"""
/api/v1/users. `/users/me` (GET) itself lives in auth.py, preserving
the exact path used since M2/M3; the rest of profile management is here.
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import User
from app.schemas import ChangePasswordRequest, MessageResponse, UpdateProfileRequest, UserRead
from app.services import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/me", response_model=UserRead)
def update_profile(
    body: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return UserService(session).update_profile(current_user, body)


@router.post("/me/change-password", response_model=MessageResponse)
def change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    UserService(session).change_password(current_user, body.current_password, body.new_password)
    return MessageResponse(message="Password changed. Please sign in again on other devices.")


@router.post("/me/deactivate", response_model=MessageResponse)
def deactivate(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    UserService(session).deactivate(current_user)
    return MessageResponse(message="Account deactivated")


@router.delete("/me", response_model=MessageResponse)
def delete_account(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    UserService(session).delete_account(current_user)
    return MessageResponse(message="Account deleted")
