from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import User
from app.schemas import NotificationRead
from app.services import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=List[NotificationRead])
def get_notifications(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return NotificationService(session).list_for_user(current_user.id)


@router.post("/read-all")
def mark_notifications_read(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    NotificationService(session).mark_all_read(current_user.id)
    return {"message": "All notifications marked as read"}
