from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlmodel import Field, Index, Relationship, SQLModel

from app.db.base import UUIDPKMixin, int_fk, uuid_fk

if TYPE_CHECKING:
    from app.models.restaurant import Restaurant
    from app.models.user import User
    from app.models.dining_session import DiningSession
    from app.models.order_item import OrderItem


class Order(UUIDPKMixin, SQLModel, table=True):
    __tablename__ = "orders"
    __table_args__ = (
        # Merchant "orders for my restaurant, by status" (KDS/queue view).
        Index("ix_orders_restaurant_status", "restaurant_id", "status"),
        # Diner's order history, newest first.
        Index("ix_orders_user_created", "user_id", "created_at"),
    )

    # SET NULL, not CASCADE/RESTRICT: an order must survive even if its
    # originating session is later removed — the order is the durable
    # financial record, the session is just how it was placed.
    session_id: Optional[UUID] = uuid_fk("dining_sessions.id", ondelete="SET NULL", nullable=True)
    user_id: Optional[UUID] = uuid_fk("users.id", ondelete="RESTRICT", nullable=True, index=False)
    restaurant_id: UUID = uuid_fk("restaurants.id", ondelete="RESTRICT", index=False)
    cart_id: Optional[int] = int_fk("carts.id", ondelete="SET NULL", nullable=True)
    customer_name: str
    customer_phone: str
    status: str = Field(default="pending")  # pending|confirmed|preparing|ready|delivered|cancelled
    special_instructions: Optional[str] = None
    subtotal: Decimal = Field(max_digits=10, decimal_places=2)
    tax: Decimal = Field(default=Decimal("0.00"), max_digits=10, decimal_places=2)
    total_amount: Decimal = Field(max_digits=10, decimal_places=2)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    restaurant: "Restaurant" = Relationship(back_populates="orders")
    user: Optional["User"] = Relationship(back_populates="orders")
    session: Optional["DiningSession"] = Relationship(back_populates="orders")
    order_items: List["OrderItem"] = Relationship(back_populates="order")
