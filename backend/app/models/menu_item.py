from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.restaurant import Restaurant
    from app.models.order_item import OrderItem

class MenuItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str
    price: float
    category: str
    image_url: Optional[str] = None
    is_available: bool = Field(default=True)
    is_vegetarian: bool = Field(default=False)
    restaurant_id: int = Field(foreign_key="restaurant.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    restaurant: Optional["Restaurant"] = Relationship(back_populates="menu_items")
    order_items: List["OrderItem"] = Relationship(back_populates="menu_item")
