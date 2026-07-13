from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Index, Relationship, SQLModel

from app.db.base import IntPKMixin, uuid_fk

if TYPE_CHECKING:
    from app.models.user import User


class Notification(IntPKMixin, SQLModel, table=True):
    __tablename__ = "notifications"
    __table_args__ = (
        # "Unread notifications for user" is the actual hot query, not
        # user_id alone.
        Index("ix_notifications_user_is_read", "user_id", "is_read"),
    )

    user_id: UUID = uuid_fk("users.id", ondelete="CASCADE", index=False)
    title: str
    body: str
    icon: str = Field(default="notifications")
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="notifications")
