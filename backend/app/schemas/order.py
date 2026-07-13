from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlmodel import SQLModel

from app.schemas.order_item import OrderItemCreate


class OrderBase(SQLModel):
    customer_name: str
    customer_phone: str
    status: str = "pending"
    special_instructions: Optional[str] = None
    restaurant_id: UUID


class OrderCreate(OrderBase):
    order_items: List[OrderItemCreate] = []
    user_id: Optional[UUID] = None
    session_id: Optional[UUID] = None


class OrderRead(OrderBase):
    id: UUID
    user_id: Optional[UUID]
    session_id: Optional[UUID]
    subtotal: Decimal
    tax: Decimal
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderStatusUpdate(SQLModel):
    status: str
