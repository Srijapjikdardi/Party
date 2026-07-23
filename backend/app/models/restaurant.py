from __future__ import annotations
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.db.base import SoftDeleteMixin, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.menu_item import MenuItem
    from app.models.menu_category import MenuCategory
    from app.models.order import Order
    from app.models.restaurant_table import RestaurantTable
    from app.models.dining_session import DiningSession
    from app.models.restaurant_staff import RestaurantStaff
    from app.models.cart import Cart


class Restaurant(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, SQLModel, table=True):
    __tablename__ = "restaurants"

    name: str = Field(index=True)
    # Ownership is expressed exclusively through RestaurantStaff
    # (role='owner'), not a direct owner_id column here — a restaurant
    # can have co-owners/managers, and duplicating "who owns this" in
    # two places (a column here + a staff table) is exactly the kind of
    # redundant data this milestone's requirements call out to avoid.
    address: str
    phone: str
    cuisine_type: str = Field(index=True)
    rating: Decimal = Field(default=Decimal("0.0"), max_digits=3, decimal_places=2)
    price_range: str = Field(default="₹300-800")
    description: str = Field(default="")
    image_url: Optional[str] = None  # Cloudinary URL once that integration lands
    is_active: bool = Field(default=True)

    menu_items: List["MenuItem"] = Relationship(back_populates="restaurant")
    menu_categories: List["MenuCategory"] = Relationship(back_populates="restaurant")
    orders: List["Order"] = Relationship(back_populates="restaurant")
    dining_sessions: List["DiningSession"] = Relationship(back_populates="restaurant")
    staff: List["RestaurantStaff"] = Relationship(back_populates="restaurant")
    carts: List["Cart"] = Relationship(back_populates="restaurant")
    tables: List["RestaurantTable"] = Relationship(back_populates="restaurant")