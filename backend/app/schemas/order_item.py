from typing import Optional

from sqlmodel import SQLModel


class OrderItemBase(SQLModel):
    quantity: int
    unit_price: float
    special_request: Optional[str] = None
    menu_item_id: int


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemRead(OrderItemBase):
    id: int
    order_id: int

    class Config:
        from_attributes = True
