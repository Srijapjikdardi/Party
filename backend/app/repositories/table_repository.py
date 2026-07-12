from typing import List, Optional

from sqlmodel import select

from app.models import Table
from app.repositories.base import BaseRepository


class TableRepository(BaseRepository[Table]):
    model = Table

    def list_by_restaurant(self, restaurant_id: int) -> List[Table]:
        return self.session.exec(select(Table).where(Table.restaurant_id == restaurant_id)).all()

    def update_status(self, table_id: int, status: str) -> Optional[Table]:
        table = self.get(table_id)
        if table:
            table.status = status
            self.add(table)
        return table
