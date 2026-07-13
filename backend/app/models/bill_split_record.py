from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.db.base import IntPKMixin, int_fk, uuid_fk

if TYPE_CHECKING:
    from app.models.bill import Bill
    from app.models.session_participant import SessionParticipant
    from app.models.payment import Payment


class BillSplitRecord(IntPKMixin, SQLModel, table=True):
    __tablename__ = "bill_split_records"
    __table_args__ = (
        UniqueConstraint("bill_id", "participant_id", name="uq_bill_split_records_bill_participant"),
    )

    bill_id: UUID = uuid_fk("bills.id", ondelete="CASCADE")
    participant_id: int = int_fk("session_participants.id", ondelete="CASCADE")
    amount_owed: Decimal = Field(max_digits=10, decimal_places=2)
    amount_paid: Decimal = Field(default=Decimal("0.00"), max_digits=10, decimal_places=2)
    status: str = Field(default="pending", index=True)  # pending | paid
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    bill: "Bill" = Relationship(back_populates="split_records")
    participant: "SessionParticipant" = Relationship(back_populates="bill_split_records")
    payments: list["Payment"] = Relationship(back_populates="bill_split_record")
