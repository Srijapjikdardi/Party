from typing import List, Optional
from uuid import UUID

from sqlmodel import Session

from app.models import DiningSession, SessionParticipant
from app.repositories import DiningSessionRepository, TableRepository
from app.schemas import DiningSessionCreate


class DiningSessionService:
    def __init__(self, session: Session):
        self.dining_sessions = DiningSessionRepository(session)
        self.tables = TableRepository(session)

    def create_session(self, data: DiningSessionCreate) -> DiningSession:
        dining_session = DiningSession(
            restaurant_id=data.restaurant_id,
            table_id=data.table_id,
            host_user_id=data.host_user_id,
        )
        dining_session = self.dining_sessions.add(dining_session)

        # Auto-add host as participant
        host_participant = SessionParticipant(session_id=dining_session.id, user_id=data.host_user_id)
        self.dining_sessions.session.add(host_participant)

        if data.table_id:
            self.tables.update_status(data.table_id, "occupied")

        self.dining_sessions.commit()
        return dining_session

    def get_session(self, session_id: UUID) -> Optional[DiningSession]:
        return self.dining_sessions.get(session_id)

    def join_session(self, session_code: str, user_id: UUID) -> Optional[DiningSession]:
        dining_session = self.dining_sessions.get_by_code(session_code)
        if not dining_session or dining_session.status != "active":
            return None

        existing = self.dining_sessions.get_participant(dining_session.id, user_id)
        if not existing:
            participant = SessionParticipant(session_id=dining_session.id, user_id=user_id)
            self.dining_sessions.add_participant(participant)

        return dining_session

    def list_participants(self, session_id: UUID) -> List[SessionParticipant]:
        return self.dining_sessions.list_participants(session_id)
