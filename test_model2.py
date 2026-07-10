from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Integer
from typing import Optional, List
from datetime import datetime

class Restaurant(SQLModel, table=True):
    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True))
    name: str = Field(index=True)
    address: str
    phone: str
    cuisine_type: str
    rating: float = Field(default=0.0, ge=0, le=5)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    menu_items: List["MenuItem"] = Relationship(back_populates="restaurant")
    orders: List["Order"] = Relationship(back_populates="restaurant")

print("Model defined")