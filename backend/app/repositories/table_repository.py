from typing import List, Optional
from uuid import UUID

from sqlmodel import select

from app.models import RestaurantTable
from app.repositories.base import BaseRepository


class TableRepository(BaseRepository[RestaurantTable]):
    model = RestaurantTable

    def list_by_restaurant(self, restaurant_id: UUID) -> List[RestaurantTable]:
        return self.session.exec(
            select(RestaurantTable).where(RestaurantTable.restaurant_id == restaurant_id)
        ).all()

    def update_status(self, table_id: UUID, status: str) -> Optional[RestaurantTable]:
        table = self.get(table_id)
        if table:
            table.status = status
            self.add(table)
        return table
