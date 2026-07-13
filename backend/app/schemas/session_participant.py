from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlmodel import SQLModel


class SessionParticipantRead(SQLModel):
    id: int
    session_id: UUID
    user_id: UUID
    share_amount: Decimal
    is_paid: bool
    joined_at: datetime

    class Config:
        from_attributes = True
