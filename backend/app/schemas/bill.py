from decimal import Decimal
from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from sqlmodel import SQLModel


class BillBase(SQLModel):
    subtotal: Decimal
    tax: Decimal = Decimal("0.00")
    service_charge: Decimal = Decimal("0.00")
    discount: Decimal = Decimal("0.00")
    total_amount: Decimal
    status: str = "pending"  # pending | split | paid
    split_type: str = "equal"  # equal | individual | host_paid


class BillCreate(BillBase):
    session_id: UUID
    custom_amounts: Optional[Dict[int, float]] = None  # participant_id -> amount (for individual split)


class BillRead(BillBase):
    id: UUID
    session_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BillGenerate(SQLModel):
    split_type: str = "equal"
    custom_amounts: Optional[Dict[int, float]] = None


class BillStatusUpdate(SQLModel):
    status: str  # pending | split | paid