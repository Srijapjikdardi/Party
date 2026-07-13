"""
Bill: the finalized total for a DiningSession, generated once ordering
is done and the table is ready to pay. Distinct from DiningSession's
running subtotal/total_amount, which tracks the live, still-changing
total while people are still ordering — Bill is the frozen snapshot
split records are computed against.
"""
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.db.base import UUIDPKMixin, uuid_fk

if TYPE_CHECKING:
    from app.models.dining_session import DiningSession
    from app.models.bill_split_record import BillSplitRecord


class Bill(UUIDPKMixin, SQLModel, table=True):
    __tablename__ = "bills"

    # One bill per session; CASCADE because a bill has no meaning
    # independent of its session.
    session_id: UUID = uuid_fk("dining_sessions.id", ondelete="CASCADE", unique=True, index=False)
    subtotal: Decimal = Field(max_digits=10, decimal_places=2)
    tax: Decimal = Field(default=Decimal("0.00"), max_digits=10, decimal_places=2)
    service_charge: Decimal = Field(default=Decimal("0.00"), max_digits=10, decimal_places=2)
    discount: Decimal = Field(default=Decimal("0.00"), max_digits=10, decimal_places=2)
    total_amount: Decimal = Field(max_digits=10, decimal_places=2)
    status: str = Field(default="pending", index=True)  # pending | split | paid
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    session: "DiningSession" = Relationship(back_populates="bill")
    split_records: List["BillSplitRecord"] = Relationship(back_populates="bill")
