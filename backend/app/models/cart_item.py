from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.db.base import IntPKMixin, int_fk, uuid_fk

if TYPE_CHECKING:
    from app.models.cart import Cart
    from app.models.menu_item import MenuItem


class CartItem(IntPKMixin, SQLModel, table=True):
    __tablename__ = "cart_items"

    cart_id: int = int_fk("carts.id", ondelete="CASCADE")
    # RESTRICT: don't let a menu item disappear out from under an
    # in-progress cart; the service layer must handle removal
    # explicitly (e.g. flag "no longer available") rather than the DB
    # silently deleting or nulling the line item.
    menu_item_id: UUID = uuid_fk("menu_items.id", ondelete="RESTRICT")
    quantity: int = Field(default=1)
    unit_price: Decimal = Field(max_digits=10, decimal_places=2)  # snapshot at add-time
    special_request: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    cart: "Cart" = Relationship(back_populates="items")
    menu_item: "MenuItem" = Relationship(back_populates="cart_items")
