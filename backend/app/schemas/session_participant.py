from datetime import datetime

from sqlmodel import SQLModel


class SessionParticipantRead(SQLModel):
    id: int
    session_id: int
    user_id: int
    share_amount: float
    is_paid: bool
    joined_at: datetime

    class Config:
        from_attributes = True
