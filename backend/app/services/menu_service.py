from typing import List
from uuid import UUID

from sqlmodel import Session

from app.models import MenuItem
from app.repositories import MenuRepository


class MenuService:
    def __init__(self, session: Session):
        self.menu = MenuRepository(session)

    def list_for_restaurant(self, restaurant_id: UUID) -> List[MenuItem]:
        return self.menu.list_by_restaurant(restaurant_id)
