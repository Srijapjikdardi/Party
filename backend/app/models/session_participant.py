from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.dining_session import DiningSession
    from app.models.user import User

class SessionParticipant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="diningsession.id")
    user_id: int = Field(foreign_key="user.id")
    share_amount: float = Field(default=0.0)
    is_paid: bool = Field(default=False)
    joined_at: datetime = Field(default_factory=datetime.utcnow)

    session: Optional["DiningSession"] = Relationship(back_populates="participants")
    user: Optional["User"] = Relationship(back_populates="session_participants")
