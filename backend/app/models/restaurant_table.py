"""
Named RestaurantTable (not Table) to avoid colliding with SQL's own
TABLE keyword and SQLAlchemy's Table class.
"""
from __future__ import annotations
from typing import List
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.db.base import TimestampMixin, UUIDPKMixin, uuid_fk


class RestaurantTable(UUIDPKMixin, TimestampMixin, SQLModel, table=True):
    __tablename__ = "restaurant_tables"
    __table_args__ = (
        UniqueConstraint("restaurant_id", "number", name="uq_restaurant_tables_restaurant_number"),
    )

    restaurant_id: UUID = uuid_fk("restaurants.id", ondelete="CASCADE")
    number: str
    capacity: int = Field(default=4)
    status: str = Field(default="available", index=True)  # available | occupied | reserved | billing
    # QR codes encode this token, not the raw PK, so a table's code can
    # be rotated (e.g. after a lost/defaced QR sticker) without
    # invalidating the table's id or its order/session history.
    qr_code_token: str = Field(unique=True, index=True)


def _set_restaurant_table_relationships():
    from app.models.restaurant import Restaurant
    from app.models.dining_session import DiningSession

    RestaurantTable.restaurant = Relationship(back_populates="tables")
    RestaurantTable.dining_sessions = Relationship(back_populates="table")


_set_restaurant_table_relationships()