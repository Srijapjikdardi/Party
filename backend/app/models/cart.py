"""
Cart: a diner's in-progress, pre-checkout selection. New in this
milestone — the app previously only had atomic Order creation with no
"add to cart, keep browsing" step.
"""
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.db.base import IntPKMixin, uuid_fk

if TYPE_CHECKING:
    from app.models.dining_session import DiningSession
    from app.models.user import User
    from app.models.restaurant import Restaurant
    from app.models.cart_item import CartItem


class Cart(IntPKMixin, SQLModel, table=True):
    __tablename__ = "carts"
    __table_args__ = (
        # One active cart per user per session — repeated "add to cart"
        # calls accumulate items in the same cart rather than creating
        # duplicates.
        UniqueConstraint("session_id", "user_id", name="uq_carts_session_user"),
    )

    # Nullable: a cart can exist outside a dining session (e.g. a future
    # takeaway/delivery flow) without schema changes.
    session_id: Optional[UUID] = uuid_fk("dining_sessions.id", ondelete="CASCADE", nullable=True)
    user_id: UUID = uuid_fk("users.id", ondelete="CASCADE")
    restaurant_id: UUID = uuid_fk("restaurants.id", ondelete="CASCADE")
    status: str = Field(default="active", index=True)  # active | checked_out | abandoned
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    session: Optional["DiningSession"] = Relationship(back_populates="carts")
    user: "User" = Relationship(back_populates="carts")
    restaurant: "Restaurant" = Relationship(back_populates="carts")
    items: List["CartItem"] = Relationship(back_populates="cart")
