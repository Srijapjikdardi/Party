from typing import List

from sqlmodel import select

from app.models import Order, OrderItem
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    model = Order

    def list_by_user(self, user_id: int) -> List[Order]:
        return self.session.exec(
            select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
        ).all()

    def list_by_restaurant(self, restaurant_id: int, limit: int = 50) -> List[Order]:
        return self.session.exec(
            select(Order)
            .where(Order.restaurant_id == restaurant_id)
            .order_by(Order.created_at.desc())
            .limit(limit)
        ).all()

    def add_order_item(self, item: OrderItem) -> OrderItem:
        self.session.add(item)
        return item
