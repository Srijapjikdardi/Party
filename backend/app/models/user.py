from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.wallet import WalletTransaction
    from app.models.notification import Notification
    from app.models.session_participant import SessionParticipant

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    phone: str = Field(unique=True, index=True)
    password_hash: str
    role: str = Field(default="diner")  # diner | merchant | waiter | admin
    avatar_url: Optional[str] = None
    wallet_balance: float = Field(default=500.0)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    orders: List["Order"] = Relationship(back_populates="user")
    wallet_transactions: List["WalletTransaction"] = Relationship(back_populates="user")
    notifications: List["Notification"] = Relationship(back_populates="user")
    session_participants: List["SessionParticipant"] = Relationship(back_populates="user")
