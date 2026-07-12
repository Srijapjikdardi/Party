from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.restaurant import Restaurant
    from app.models.user import User
    from app.models.order_item import OrderItem

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    customer_name: str
    customer_phone: str
    total_amount: float
    status: str = Field(default="pending")  # pending | confirmed | preparing | ready | delivered | cancelled
    special_instructions: Optional[str] = None
    restaurant_id: int = Field(foreign_key="restaurant.id")
    session_id: Optional[int] = Field(default=None, foreign_key="diningsession.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    restaurant: Optional["Restaurant"] = Relationship(back_populates="orders")
    user: Optional["User"] = Relationship(back_populates="orders")
    order_items: List["OrderItem"] = Relationship(back_populates="order")
