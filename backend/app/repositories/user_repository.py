from typing import Optional

from sqlmodel import select

from app.models import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def get_by_email(self, email: str) -> Optional[User]:
        """Excludes soft-deleted users — for login and anything that
        should treat a deleted account as not existing."""
        return self.session.exec(
            select(User).where(User.email == email, User.deleted_at.is_(None))
        ).first()

    def get_by_email_including_deleted(self, email: str) -> Optional[User]:
        """A soft-deleted user still holds the DB's UNIQUE(email)
        constraint — used by registration's duplicate check so a
        re-registration attempt gets a clean 400 instead of an
        unhandled IntegrityError from the INSERT itself."""
        return self.session.exec(select(User).where(User.email == email)).first()

    def get_by_phone(self, phone: str) -> Optional[User]:
        return self.session.exec(
            select(User).where(User.phone == phone, User.deleted_at.is_(None))
        ).first()

    def get_by_google_id(self, google_id: str) -> Optional[User]:
        return self.session.exec(
            select(User).where(User.google_id == google_id, User.deleted_at.is_(None))
        ).first()

    def get_by_apple_id(self, apple_id: str) -> Optional[User]:
        return self.session.exec(
            select(User).where(User.apple_id == apple_id, User.deleted_at.is_(None))
        ).first()
