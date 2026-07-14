from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlmodel import SQLModel


class UserRead(SQLModel):
    """Never includes password_hash or raw tokens — see docs/AUTHENTICATION.md
    'No sensitive data in API responses'."""
    id: UUID
    name: str
    email: str
    phone: str
    role: str
    avatar_url: Optional[str]
    wallet_balance: Decimal
    is_active: bool
    is_email_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True
