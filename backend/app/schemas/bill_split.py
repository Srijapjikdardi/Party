from decimal import Decimal
from uuid import UUID

from sqlmodel import SQLModel


class BillSplitBase(SQLModel):
    amount_owed: Decimal
    amount_paid: Decimal = Decimal("0.00")
    status: str = "pending"  # pending | paid | partial


class BillSplitCreate(BillSplitBase):
    bill_id: UUID
    participant_id: int


class BillSplitRead(BillSplitBase):
    id: int
    bill_id: UUID
    participant_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BillSplitUpdate(SQLModel):
    amount_paid: Decimal
    status: str