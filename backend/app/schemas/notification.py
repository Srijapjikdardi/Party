from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel


class NotificationRead(SQLModel):
    id: int
    user_id: UUID
    title: str
    body: str
    icon: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
