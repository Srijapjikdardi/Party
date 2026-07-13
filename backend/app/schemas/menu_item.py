from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlmodel import SQLModel


class MenuItemBase(SQLModel):
    name: str
    description: str
    price: Decimal
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    is_available: bool = True
    is_vegetarian: bool = False


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemRead(MenuItemBase):
    id: UUID
    restaurant_id: UUID
    # Read-only convenience: the joined category name, computed on read
    # via MenuItem.category_name (see app/models/menu_item.py) rather
    # than stored — avoids duplicating the category name on every item.
    category_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
