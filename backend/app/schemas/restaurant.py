from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlmodel import SQLModel


class RestaurantBase(SQLModel):
    name: str
    address: str
    phone: str
    cuisine_type: str
    rating: Decimal = Decimal("0.0")
    price_range: str = "₹300-800"
    description: str = ""
    image_url: Optional[str] = None
    is_active: bool = True


class RestaurantCreate(RestaurantBase):
    pass


class RestaurantRead(RestaurantBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
