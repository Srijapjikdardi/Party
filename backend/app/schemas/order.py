from datetime import datetime
from typing import List, Optional

from sqlmodel import SQLModel

from app.schemas.order_item import OrderItemCreate


class OrderBase(SQLModel):
    customer_name: str
    customer_phone: str
    total_amount: float
    status: str = "pending"
    special_instructions: Optional[str] = None
    restaurant_id: int


class OrderCreate(OrderBase):
    order_items: List[OrderItemCreate] = []
    user_id: Optional[int] = None
    session_id: Optional[int] = None


class OrderRead(OrderBase):
    id: int
    user_id: Optional[int]
    session_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderStatusUpdate(SQLModel):
    status: str
