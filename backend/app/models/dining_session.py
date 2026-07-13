import secrets
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlmodel import Field, Index, Relationship, SQLModel

from app.db.base import UUIDPKMixin, uuid_fk

if TYPE_CHECKING:
    from app.models.restaurant import Restaurant
    from app.models.restaurant_table import RestaurantTable
    from app.models.session_participant import SessionParticipant
    from app.models.cart import Cart
    from app.models.order import Order
    from app.models.bill import Bill


class DiningSession(UUIDPKMixin, SQLModel, table=True):
    __tablename__ = "dining_sessions"
    __table_args__ = (
        # Merchant dashboard's main query: "active sessions at my restaurant".
        Index("ix_dining_sessions_restaurant_status", "restaurant_id", "status"),
    )

    # RESTRICT: a restaurant with session history can't be hard-deleted
    # out from under it (soft-delete the restaurant instead).
    restaurant_id: UUID = uuid_fk("restaurants.id", ondelete="RESTRICT", index=False)
    # SET NULL: reassigning/removing a table shouldn't destroy session
    # history that already happened at it.
    table_id: Optional[UUID] = uuid_fk("restaurant_tables.id", ondelete="SET NULL", nullable=True)
    host_user_id: UUID = uuid_fk("users.id", ondelete="RESTRICT")
    # Short human-shareable code (spoken/typed to join), distinct from
    # the UUID primary key used in URLs/QR payloads.
    session_code: str = Field(default_factory=lambda: secrets.token_hex(3).upper(), unique=True, index=True)
    status: str = Field(default="active", index=True)  # active | billing | closed
    subtotal: Decimal = Field(default=Decimal("0.00"), max_digits=10, decimal_places=2)
    tax: Decimal = Field(default=Decimal("0.00"), max_digits=10, decimal_places=2)
    service_charge: Decimal = Field(default=Decimal("0.00"), max_digits=10, decimal_places=2)
    total_amount: Decimal = Field(default=Decimal("0.00"), max_digits=10, decimal_places=2)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None

    restaurant: "Restaurant" = Relationship(back_populates="dining_sessions")
    table: Optional["RestaurantTable"] = Relationship(back_populates="dining_sessions")
    participants: List["SessionParticipant"] = Relationship(back_populates="session")
    carts: List["Cart"] = Relationship(back_populates="session")
    orders: List["Order"] = Relationship(back_populates="session")
    bill: Optional["Bill"] = Relationship(back_populates="session")
