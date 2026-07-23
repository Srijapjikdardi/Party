"""
Small static lookup table: owner | manager | waiter | chef | cashier.
Seeded once (see app/seed.py), read-heavy, essentially never written to
after setup — a plain small int-PK table, no need for anything fancier.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.db.base import IntPKMixin

from app.models.restaurant_staff import RestaurantStaff


class RestaurantRole(IntPKMixin, SQLModel, table=True):
    __tablename__ = "restaurant_roles"

    name: str = Field(unique=True, index=True)  # owner | manager | waiter | chef | cashier
    description: Optional[str] = None

    staff: List[RestaurantStaff] = Relationship(back_populates="role")
