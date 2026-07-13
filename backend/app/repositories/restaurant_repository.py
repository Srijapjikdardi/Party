from typing import List, Optional

from sqlmodel import select

from app.models import Restaurant
from app.repositories.base import BaseRepository


class RestaurantRepository(BaseRepository[Restaurant]):
    model = Restaurant

    def list(self, skip: int = 0, limit: int = 100, cuisine: Optional[str] = None) -> List[Restaurant]:
        query = (
            select(Restaurant)
            .where(Restaurant.is_active == True, Restaurant.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        if cuisine:
            query = query.where(Restaurant.cuisine_type == cuisine)
        return self.session.exec(query).all()
