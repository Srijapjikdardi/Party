"""
One row per gateway event (created/authorized/captured/failed/refunded)
for a Payment — an append-only audit log, not something the app
mutates. `gateway_transaction_id` carries the uniqueness constraint
that makes webhook processing idempotent (a retried webhook for the
same gateway transaction id is a no-op, not a duplicate row).
"""
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.db.base import IntPKMixin, uuid_fk

if TYPE_CHECKING:
    from app.models.payment import Payment


class PaymentTransaction(IntPKMixin, SQLModel, table=True):
    __tablename__ = "payment_transactions"

    payment_id: UUID = uuid_fk("payments.id", ondelete="CASCADE")
    gateway_transaction_id: Optional[str] = Field(default=None, unique=True, index=True)
    event_type: str = Field(index=True)  # created|authorized|captured|failed|refunded
    amount: Decimal = Field(max_digits=10, decimal_places=2)
    raw_payload: Optional[str] = None  # gateway webhook payload (JSON text), kept for audit/debugging
    created_at: datetime = Field(default_factory=datetime.utcnow)

    payment: "Payment" = Relationship(back_populates="transactions")
