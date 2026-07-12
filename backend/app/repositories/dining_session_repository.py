from typing import List, Optional

from sqlmodel import select

from app.models import DiningSession, SessionParticipant
from app.repositories.base import BaseRepository


class DiningSessionRepository(BaseRepository[DiningSession]):
    model = DiningSession

    def get_by_code(self, code: str) -> Optional[DiningSession]:
        return self.session.exec(select(DiningSession).where(DiningSession.session_code == code)).first()

    def list_participants(self, session_id: int) -> List[SessionParticipant]:
        return self.session.exec(
            select(SessionParticipant).where(SessionParticipant.session_id == session_id)
        ).all()

    def get_participant(self, session_id: int, user_id: int) -> Optional[SessionParticipant]:
        return self.session.exec(
            select(SessionParticipant).where(
                SessionParticipant.session_id == session_id,
                SessionParticipant.user_id == user_id,
            )
        ).first()

    def add_participant(self, participant: SessionParticipant) -> SessionParticipant:
        self.session.add(participant)
        self.session.commit()
        self.session.refresh(participant)
        return participant
