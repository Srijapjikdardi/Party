from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlmodel import SQLModel


class OrderItemBase(SQLModel):
    quantity: int
    unit_price: Decimal
    special_request: Optional[str] = None
    menu_item_id: UUID


class OrderItemCreate(SQLModel):
    quantity: int
    special_request: Optional[str] = None
    menu_item_id: UUID


class OrderItemRead(OrderItemBase):
    id: int
    order_id: UUID

    class Config:
        from_attributes = True
