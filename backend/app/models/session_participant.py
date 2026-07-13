from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.db.base import IntPKMixin, uuid_fk

if TYPE_CHECKING:
    from app.models.dining_session import DiningSession
    from app.models.user import User
    from app.models.bill_split_record import BillSplitRecord


class SessionParticipant(IntPKMixin, SQLModel, table=True):
    __tablename__ = "session_participants"
    __table_args__ = (
        # DB-enforced: a user can't join the same session twice (was
        # only an application-level check before this milestone).
        UniqueConstraint("session_id", "user_id", name="uq_session_participants_session_user"),
    )

    session_id: UUID = uuid_fk("dining_sessions.id", ondelete="CASCADE")
    # RESTRICT: keep the user row (soft-deletable) rather than silently
    # losing who was at a historical session.
    user_id: UUID = uuid_fk("users.id", ondelete="RESTRICT")
    share_amount: Decimal = Field(default=Decimal("0.00"), max_digits=10, decimal_places=2)
    is_paid: bool = Field(default=False)
    joined_at: datetime = Field(default_factory=datetime.utcnow)

    session: "DiningSession" = Relationship(back_populates="participants")
    user: "User" = Relationship(back_populates="session_participants")
    bill_split_records: list["BillSplitRecord"] = Relationship(back_populates="participant")
