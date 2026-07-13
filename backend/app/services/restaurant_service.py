from typing import List, Optional
from uuid import UUID

from sqlmodel import Session

from app.models import Restaurant
from app.repositories import RestaurantRepository


class RestaurantService:
    def __init__(self, session: Session):
        self.restaurants = RestaurantRepository(session)

    def list_restaurants(self, skip: int = 0, limit: int = 100, cuisine: Optional[str] = None) -> List[Restaurant]:
        return self.restaurants.list(skip=skip, limit=limit, cuisine=cuisine)

    def get_restaurant(self, restaurant_id: UUID) -> Optional[Restaurant]:
        return self.restaurants.get(restaurant_id)
