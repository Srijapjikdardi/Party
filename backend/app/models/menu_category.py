from typing import TYPE_CHECKING, List
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.db.base import IntPKMixin, uuid_fk

if TYPE_CHECKING:
    from app.models.restaurant import Restaurant
    from app.models.menu_item import MenuItem


class MenuCategory(IntPKMixin, SQLModel, table=True):
    __tablename__ = "menu_categories"
    __table_args__ = (
        UniqueConstraint("restaurant_id", "name", name="uq_menu_categories_restaurant_name"),
    )

    restaurant_id: UUID = uuid_fk("restaurants.id", ondelete="CASCADE")
    name: str
    display_order: int = Field(default=0)

    restaurant: "Restaurant" = Relationship(back_populates="menu_categories")
    menu_items: List["MenuItem"] = Relationship(back_populates="category")
