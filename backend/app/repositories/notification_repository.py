from typing import List

from sqlmodel import select

from app.models import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    model = Notification

    def list_by_user(self, user_id: int) -> List[Notification]:
        return self.session.exec(
            select(Notification).where(Notification.user_id == user_id).order_by(Notification.created_at.desc())
        ).all()

    def list_unread(self, user_id: int) -> List[Notification]:
        return self.session.exec(
            select(Notification).where(
                Notification.user_id == user_id,
                Notification.is_read == False,
            )
        ).all()
