from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlmodel import SQLModel


class UserCreate(SQLModel):
    name: str
    email: str
    phone: str
    password: str
    role: str = "diner"


class UserRead(SQLModel):
    id: UUID
    name: str
    email: str
    phone: str
    role: str
    avatar_url: Optional[str]
    wallet_balance: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(SQLModel):
    email: str
    password: str
