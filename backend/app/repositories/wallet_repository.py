from typing import List

from sqlmodel import select

from app.models import WalletTransaction
from app.repositories.base import BaseRepository


class WalletRepository(BaseRepository[WalletTransaction]):
    model = WalletTransaction

    def list_by_user(self, user_id: int, limit: int = 20) -> List[WalletTransaction]:
        return self.session.exec(
            select(WalletTransaction)
            .where(WalletTransaction.user_id == user_id)
            .order_by(WalletTransaction.created_at.desc())
            .limit(limit)
        ).all()
