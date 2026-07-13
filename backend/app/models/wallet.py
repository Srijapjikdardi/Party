from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.db.base import IntPKMixin, uuid_fk

if TYPE_CHECKING:
    from app.models.user import User


class WalletTransaction(IntPKMixin, SQLModel, table=True):
    __tablename__ = "wallet_transactions"

    user_id: UUID = uuid_fk("users.id", ondelete="CASCADE")
    amount: Decimal = Field(max_digits=10, decimal_places=2)
    transaction_type: str = Field(index=True)  # credit | debit
    description: str
    reference_id: Optional[str] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="wallet_transactions")
