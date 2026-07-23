from __future__ import annotations
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.db.base import SoftDeleteMixin, TimestampMixin, UUIDPKMixin, int_fk, uuid_fk

from app.models.restaurant import Restaurant
from app.models.menu_category import MenuCategory
from app.models.order_item import OrderItem
from app.models.cart_item import CartItem

class MenuItem(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, SQLModel, table=True):
    __tablename__ = "menu_items"

    restaurant_id: UUID = uuid_fk("restaurants.id", ondelete="CASCADE")
    # SET NULL, not CASCADE: removing a category shouldn't delete the
    # dishes in it — they become "uncategorized" instead.
    category_id: Optional[int] = int_fk("menu_categories.id", ondelete="SET NULL", nullable=True)
    name: str = Field(index=True)
    description: str
    price: Decimal = Field(max_digits=10, decimal_places=2)
    image_url: Optional[str] = None  # Cloudinary URL once that integration lands
    is_available: bool = Field(default=True)
    is_vegetarian: bool = Field(default=False)

    restaurant: Restaurant = Relationship(back_populates="menu_items")
    category: Optional[MenuCategory] = Relationship(back_populates="menu_items")
    order_items: List[OrderItem] = Relationship(back_populates="menu_item")
    cart_items: List[CartItem] = Relationship(back_populates="menu_item")

    @property
    def category_name(self) -> Optional[str]:
        return self.category.name if self.category else None
