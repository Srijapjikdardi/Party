from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import select

from app.models import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    model = RefreshToken

    def get_by_hash(self, token_hash: str) -> Optional[RefreshToken]:
        return self.session.exec(select(RefreshToken).where(RefreshToken.token_hash == token_hash)).first()

    def list_active_for_user(self, user_id: UUID) -> List[RefreshToken]:
        return self.session.exec(
            select(RefreshToken).where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        ).all()

    def revoke(self, token: RefreshToken) -> None:
        token.revoked_at = datetime.utcnow()
        self.session.add(token)
        self.session.commit()

    def revoke_all_for_user(self, user_id: UUID) -> None:
        for token in self.list_active_for_user(user_id):
            token.revoked_at = datetime.utcnow()
            self.session.add(token)
        self.session.commit()
