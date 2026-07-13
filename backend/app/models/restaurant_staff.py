"""
Normalizes "who works at which restaurant, with what role" — replaces
a direct Restaurant.owner_id column. A restaurant can have many staff;
a user can staff many restaurants (e.g. a waiter who picks up shifts
at two locations).
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.db.base import IntPKMixin, int_fk, uuid_fk

if TYPE_CHECKING:
    from app.models.restaurant import Restaurant
    from app.models.user import User
    from app.models.restaurant_role import RestaurantRole


class RestaurantStaff(IntPKMixin, SQLModel, table=True):
    __tablename__ = "restaurant_staff"
    __table_args__ = (
        # One membership row per (restaurant, user) — a person has
        # exactly one role at a given restaurant at a time.
        UniqueConstraint("restaurant_id", "user_id", name="uq_restaurant_staff_restaurant_user"),
    )

    restaurant_id: UUID = uuid_fk("restaurants.id", ondelete="CASCADE")
    user_id: UUID = uuid_fk("users.id", ondelete="CASCADE")
    role_id: int = int_fk("restaurant_roles.id", ondelete="RESTRICT")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    restaurant: Optional["Restaurant"] = Relationship(back_populates="staff")
    user: Optional["User"] = Relationship(back_populates="staff_memberships")
    role: Optional["RestaurantRole"] = Relationship(back_populates="staff")
