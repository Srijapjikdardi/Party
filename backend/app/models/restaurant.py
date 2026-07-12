from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.menu_item import MenuItem
    from app.models.order import Order
    from app.models.table import Table
    from app.models.dining_session import DiningSession

class Restaurant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    address: str
    phone: str
    cuisine_type: str
    rating: float = Field(default=0.0, ge=0, le=5)
    price_range: str = Field(default="₹300-800")
    description: str = Field(default="")
    image_url: Optional[str] = None
    is_active: bool = Field(default=True)
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    menu_items: List["MenuItem"] = Relationship(back_populates="restaurant")
    orders: List["Order"] = Relationship(back_populates="restaurant")
    tables: List["Table"] = Relationship(back_populates="restaurant")
    dining_sessions: List["DiningSession"] = Relationship(back_populates="restaurant")
