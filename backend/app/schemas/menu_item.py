from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel


class MenuItemBase(SQLModel):
    name: str
    description: str
    price: float
    category: str
    image_url: Optional[str] = None
    is_available: bool = True
    is_vegetarian: bool = False


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemRead(MenuItemBase):
    id: int
    restaurant_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
