from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel


class DiningSessionCreate(SQLModel):
    restaurant_id: int
    table_id: Optional[int] = None
    host_user_id: int


class DiningSessionRead(SQLModel):
    id: int
    restaurant_id: int
    table_id: Optional[int]
    host_user_id: int
    session_code: str
    status: str
    total_amount: float
    created_at: datetime

    class Config:
        from_attributes = True
