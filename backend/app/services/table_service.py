from typing import List, Optional
from uuid import UUID

from sqlmodel import Session

from app.models import RestaurantTable
from app.repositories import TableRepository


class TableService:
    def __init__(self, session: Session):
        self.tables = TableRepository(session)

    def list_for_restaurant(self, restaurant_id: UUID) -> List[RestaurantTable]:
        return self.tables.list_by_restaurant(restaurant_id)

    def update_status(self, table_id: UUID, status: str) -> Optional[RestaurantTable]:
        return self.tables.update_status(table_id, status)
