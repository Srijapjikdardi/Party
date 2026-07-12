from datetime import datetime
from typing import List, Optional

from sqlmodel import Session

from app.models import Order, OrderItem
from app.repositories import OrderRepository
from app.schemas import OrderCreate


class OrderService:
    def __init__(self, session: Session):
        self.orders = OrderRepository(session)

    def create_order(self, data: OrderCreate) -> Order:
        order_dict = data.dict()
        order_items = order_dict.pop("order_items", [])

        db_order = Order(**order_dict)
        db_order = self.orders.add(db_order)

        for item in order_items:
            item["order_id"] = db_order.id
            self.orders.add_order_item(OrderItem(**item))
        self.orders.commit()
        self.orders.session.refresh(db_order)

        return db_order

    def get_order(self, order_id: int) -> Optional[Order]:
        return self.orders.get(order_id)

    def list_for_user(self, user_id: int) -> List[Order]:
        return self.orders.list_by_user(user_id)

    def list_for_restaurant(self, restaurant_id: int, limit: int = 50) -> List[Order]:
        return self.orders.list_by_restaurant(restaurant_id, limit)

    def update_status(self, order_id: int, status: str) -> Optional[Order]:
        order = self.orders.get(order_id)
        if order:
            order.status = status
            order.updated_at = datetime.utcnow()
            self.orders.add(order)
        return order

    def restaurant_analytics(self, restaurant_id: int) -> dict:
        orders = self.orders.list_by_restaurant(restaurant_id, limit=200)
        total_revenue = sum(o.total_amount for o in orders)
        delivered = [o for o in orders if o.status == "delivered"]
        pending = [o for o in orders if o.status in ("pending", "confirmed", "preparing")]
        return {
            "total_revenue": total_revenue,
            "total_orders": len(orders),
            "delivered_orders": len(delivered),
            "pending_orders": len(pending),
            "avg_order_value": total_revenue / len(orders) if orders else 0,
        }
