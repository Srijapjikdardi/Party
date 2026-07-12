from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.menu_item import MenuItem

class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quantity: int
    unit_price: float
    special_request: Optional[str] = None
    order_id: int = Field(foreign_key="order.id")
    menu_item_id: int = Field(foreign_key="menuitem.id")

    order: Optional["Order"] = Relationship(back_populates="order_items")
    menu_item: Optional["MenuItem"] = Relationship(back_populates="order_items")
