from typing import List

from sqlmodel import Session

from app.models import Notification
from app.repositories import NotificationRepository


class NotificationService:
    def __init__(self, session: Session):
        self.notifications = NotificationRepository(session)

    def list_for_user(self, user_id: int) -> List[Notification]:
        return self.notifications.list_by_user(user_id)

    def mark_all_read(self, user_id: int) -> None:
        for notif in self.notifications.list_unread(user_id):
            notif.is_read = True
            self.notifications.session.add(notif)
        self.notifications.commit()
