from typing import List
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.models import MenuItem
from app.repositories.base import BaseRepository


class MenuRepository(BaseRepository[MenuItem]):
    model = MenuItem

    def list_by_restaurant(self, restaurant_id: UUID) -> List[MenuItem]:
        # selectinload: one extra query for all categories instead of
        # one lazy-loaded query per item when the service reads
        # `item.category_name` for each row in the response.
        statement = (
            select(MenuItem)
            .where(
                MenuItem.restaurant_id == restaurant_id,
                MenuItem.is_available == True,
                MenuItem.deleted_at.is_(None),
            )
            .options(selectinload(MenuItem.category))
        )
        return self.session.exec(statement).all()
