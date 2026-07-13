from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlmodel import SQLModel


class WalletTransactionRead(SQLModel):
    id: int
    user_id: UUID
    amount: Decimal
    transaction_type: str
    description: str
    reference_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class WalletTopup(SQLModel):
    amount: Decimal
    payment_method: str = "upi"
