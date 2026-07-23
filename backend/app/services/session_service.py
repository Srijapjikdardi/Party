from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select, func, select, func

from app.models import DiningSession, SessionParticipant
from app.repositories import DiningSessionRepository, TableRepository
from app.schemas import DiningSessionCreate
from app.services.bill_service import BillService


class DiningSessionService:
    def __init__(self, session: Session):
        self.session = session
        self.dining_sessions = DiningSessionRepository(session)
        self.tables = TableRepository(session)
        self.bill_service = BillService(session)

    def create_session(self, data: DiningSessionCreate) -> DiningSession:
        dining_session = DiningSession(
            restaurant_id=data.restaurant_id,
            table_id=data.table_id,
            host_user_id=data.host_user_id,
        )
        dining_session = self.dining_sessions.add(dining_session)

        # Auto-add host as participant
        host_participant = SessionParticipant(session_id=dining_session.id, user_id=data.host_user_id)
        self.session.add(host_participant)
        self.session.commit()
        self.session.refresh(dining_session)
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
            self.session.add(participant)
            self.session.commit()
            self.session.refresh(participant)

        return dining_session

    def list_participants(self, session_id: UUID) -> List[SessionParticipant]:
        return self.dining_sessions.list_participants(session_id)

    def list_by_user(self, user_id: UUID) -> List[DiningSession]:
        return self.dining_sessions.list_by_user(user_id)

    def generate_bill(self, session_id: UUID) -> dict:
        """Generate a bill for the session and return bill info."""
        bill = self.bill_service.generate_bill_for_session(session_id)
        # Update session status to billing
        session = self.dining_sessions.get(session_id)
        if session:
            session.status = "billing"
            self.session.add(session)
            self.session.commit()
            self.session.refresh(session)
        return {
            "bill_id": bill.id,
            "total_amount": bill.total_amount,
            "status": bill.status,
        }

    def close_session(self, session_id: UUID) -> DiningSession:
        """Mark session as closed after bill paid."""
        session = self.dining_sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")
        session.status = "closed"
        session.closed_at = datetime.utcnow()
        self.session.add(session)
        self.session.commit()
        self.session.refresh(session)
        return session