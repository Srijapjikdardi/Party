from typing import List

from sqlmodel import select

from app.models import MenuItem
from app.repositories.base import BaseRepository


class MenuRepository(BaseRepository[MenuItem]):
    model = MenuItem

    def list_by_restaurant(self, restaurant_id: int) -> List[MenuItem]:
        statement = select(MenuItem).where(
            MenuItem.restaurant_id == restaurant_id,
            MenuItem.is_available == True,
        )
        return self.session.exec(statement).all()
