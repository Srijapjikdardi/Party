"""
Payment: one payment attempt/intent. `purpose` distinguishes what it's
for so this single table serves bill-splitting, wallet top-ups, and
future direct order payments without three near-identical tables.
`bill_split_record_id` is nullable because wallet top-ups aren't tied
to a bill.
"""
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlmodel import Field, Index, Relationship, SQLModel

from app.db.base import UUIDPKMixin, int_fk, uuid_fk

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.bill_split_record import BillSplitRecord
    from app.models.payment_transaction import PaymentTransaction


class Payment(UUIDPKMixin, SQLModel, table=True):
    __tablename__ = "payments"
    __table_args__ = (
        Index("ix_payments_user_status", "user_id", "status"),
    )

    user_id: UUID = uuid_fk("users.id", ondelete="RESTRICT", index=False)
    bill_split_record_id: Optional[int] = int_fk(
        "bill_split_records.id", ondelete="SET NULL", nullable=True
    )
    purpose: str = Field(index=True)  # bill_split | wallet_topup | order_payment
    amount: Decimal = Field(max_digits=10, decimal_places=2)
    currency: str = Field(default="INR")
    method: str = Field(default="upi")  # wallet | upi | card | netbanking
    status: str = Field(default="pending", index=True)  # pending|success|failed|refunded
    gateway: str = Field(default="internal")  # internal | razorpay
    gateway_order_id: Optional[str] = Field(default=None, unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    user: "User" = Relationship(back_populates="payments")
    bill_split_record: Optional["BillSplitRecord"] = Relationship(back_populates="payments")
    transactions: List["PaymentTransaction"] = Relationship(back_populates="payment")