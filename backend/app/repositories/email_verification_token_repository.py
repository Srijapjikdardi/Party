from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import select

from app.models import EmailVerificationToken
from app.repositories.base import BaseRepository


class EmailVerificationTokenRepository(BaseRepository[EmailVerificationToken]):
    model = EmailVerificationToken

    def get_by_hash(self, token_hash: str) -> Optional[EmailVerificationToken]:
        return self.session.exec(
            select(EmailVerificationToken).where(EmailVerificationToken.token_hash == token_hash)
        ).first()

    def invalidate_unused_for_user(self, user_id: UUID) -> None:
        """Called before issuing a new token so only the most recent
        one a user was emailed is ever valid (resend shouldn't leave
        old links usable)."""
        pending = self.session.exec(
            select(EmailVerificationToken).where(
                EmailVerificationToken.user_id == user_id,
                EmailVerificationToken.used_at.is_(None),
            )
        ).all()
        for token in pending:
            token.used_at = datetime.utcnow()
            self.session.add(token)
        self.session.commit()
