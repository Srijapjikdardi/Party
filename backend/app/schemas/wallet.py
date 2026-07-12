from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel


class WalletTransactionRead(SQLModel):
    id: int
    user_id: int
    amount: float
    transaction_type: str
    description: str
    reference_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class WalletTopup(SQLModel):
    amount: float
    payment_method: str = "upi"
