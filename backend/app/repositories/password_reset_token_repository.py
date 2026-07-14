from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import select

from app.models import PasswordResetToken
from app.repositories.base import BaseRepository


class PasswordResetTokenRepository(BaseRepository[PasswordResetToken]):
    model = PasswordResetToken

    def get_by_hash(self, token_hash: str) -> Optional[PasswordResetToken]:
        return self.session.exec(
            select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
        ).first()

    def invalidate_unused_for_user(self, user_id: UUID) -> None:
        pending = self.session.exec(
            select(PasswordResetToken).where(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.used_at.is_(None),
            )
        ).all()
        for token in pending:
            token.used_at = datetime.utcnow()
            self.session.add(token)
        self.session.commit()
