from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.restaurant import Restaurant
    from app.models.dining_session import DiningSession

class Table(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    restaurant_id: int = Field(foreign_key="restaurant.id")
    number: str
    capacity: int = Field(default=4)
    status: str = Field(default="available")  # available | occupied | reserved | billing

    restaurant: Optional["Restaurant"] = Relationship(back_populates="tables")
    dining_sessions: List["DiningSession"] = Relationship(back_populates="table")
