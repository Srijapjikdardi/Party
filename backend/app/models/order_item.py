from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel
from decimal import Decimal

from app.db.base import IntPKMixin, uuid_fk

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.menu_item import MenuItem


class OrderItem(IntPKMixin, SQLModel, table=True):
    __tablename__ = "order_items"

    order_id: UUID = uuid_fk("orders.id", ondelete="CASCADE")
    # RESTRICT: a discontinued dish must not silently delete historical
    # order line items — MenuItem uses soft delete precisely so this
    # reference stays valid.
    menu_item_id: UUID = uuid_fk("menu_items.id", ondelete="RESTRICT")
    quantity: int
    unit_price: Decimal = Field(max_digits=10, decimal_places=2)  # snapshot at order-time
    special_request: Optional[str] = None

    order: "Order" = Relationship(back_populates="order_items")
    menu_item: "MenuItem" = Relationship(back_populates="order_items")
