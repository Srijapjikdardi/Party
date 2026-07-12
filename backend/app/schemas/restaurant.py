from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel


class RestaurantBase(SQLModel):
    name: str
    address: str
    phone: str
    cuisine_type: str
    rating: float = 0.0
    price_range: str = "₹300-800"
    description: str = ""
    image_url: Optional[str] = None
    is_active: bool = True


class RestaurantCreate(RestaurantBase):
    pass


class RestaurantRead(RestaurantBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
