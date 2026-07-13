from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlmodel import SQLModel


class DiningSessionCreate(SQLModel):
    restaurant_id: UUID
    table_id: Optional[UUID] = None
    host_user_id: UUID


class DiningSessionRead(SQLModel):
    id: UUID
    restaurant_id: UUID
    table_id: Optional[UUID]
    host_user_id: UUID
    session_code: str
    status: str
    total_amount: Decimal
    created_at: datetime

    class Config:
        from_attributes = True
