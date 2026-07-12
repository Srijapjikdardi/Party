from typing import List, Optional

from sqlmodel import Session

from app.models import Table
from app.repositories import TableRepository


class TableService:
    def __init__(self, session: Session):
        self.tables = TableRepository(session)

    def list_for_restaurant(self, restaurant_id: int) -> List[Table]:
        return self.tables.list_by_restaurant(restaurant_id)

    def update_status(self, table_id: int, status: str) -> Optional[Table]:
        return self.tables.update_status(table_id, status)
