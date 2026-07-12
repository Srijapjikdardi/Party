import secrets
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.restaurant import Restaurant
    from app.models.table import Table
    from app.models.session_participant import SessionParticipant

class DiningSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    restaurant_id: int = Field(foreign_key="restaurant.id")
    table_id: Optional[int] = Field(default=None, foreign_key="table.id")
    host_user_id: int = Field(foreign_key="user.id")
    session_code: str = Field(default_factory=lambda: secrets.token_hex(3).upper())
    status: str = Field(default="active")  # active | billing | closed
    total_amount: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None

    restaurant: Optional["Restaurant"] = Relationship(back_populates="dining_sessions")
    table: Optional["Table"] = Relationship(back_populates="dining_sessions")
    participants: List["SessionParticipant"] = Relationship(back_populates="session")
