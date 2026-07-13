from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import User
from app.schemas import DiningSessionCreate, DiningSessionRead, SessionParticipantRead
from app.services import DiningSessionService

router = APIRouter(prefix="/sessions", tags=["dining-sessions"])


@router.post("", response_model=DiningSessionRead)
def create_session(data: DiningSessionCreate, session: Session = Depends(get_session)):
    return DiningSessionService(session).create_session(data)


@router.get("/{session_id}", response_model=DiningSessionRead)
def get_session_by_id(session_id: UUID, session: Session = Depends(get_session)):
    ds = DiningSessionService(session).get_session(session_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Session not found")
    return ds


@router.post("/join/{session_code}", response_model=DiningSessionRead)
def join_session(
    session_code: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    ds = DiningSessionService(session).join_session(session_code.upper(), current_user.id)
    if not ds:
        raise HTTPException(status_code=404, detail="Session not found or not active")
    return ds


@router.get("/{session_id}/participants", response_model=List[SessionParticipantRead])
def get_participants(session_id: UUID, session: Session = Depends(get_session)):
    return DiningSessionService(session).list_participants(session_id)
