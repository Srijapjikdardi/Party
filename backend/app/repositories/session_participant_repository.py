from typing import List, Optional
from uuid import UUID

from sqlmodel import select

from app.models import SessionParticipant
from app.repositories.base import BaseRepository


class SessionParticipantRepository(BaseRepository[SessionParticipant]):
    model = SessionParticipant

    def list_by_session(self, session_id: UUID) -> List[SessionParticipant]:
        return self.session.exec(
            select(SessionParticipant).where(SessionParticipant.session_id == session_id)
        ).all()

    def get_by_user_and_session(self, user_id: UUID, session_id: UUID) -> Optional[SessionParticipant]:
        return self.session.exec(
            select(SessionParticipant).where(
                SessionParticipant.user_id == user_id,
                SessionParticipant.session_id == session_id
            )
        ).first()