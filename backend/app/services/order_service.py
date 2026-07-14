from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from app.core.errors import AppError
from app.models import MenuItem, Order, OrderItem
from app.repositories import OrderRepository
from app.schemas import OrderCreate
from app.schemas.order_item import OrderItemCreate


class OrderError(AppError):
    """Raised for order-creation failures the API layer should turn into 4xx responses."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(status_code, "order_error", message)


class OrderService:
    def __init__(self, session: Session):
        self.session = session
        self.orders = OrderRepository(session)

    def create_order(self, data: OrderCreate) -> Order:
        # Prices are always taken from the current MenuItem row, never
        # from the request body — the old schema let the client send
        # `total_amount`/`unit_price` directly, meaning a diner's
        # browser could set its own price. Server-computed pricing
        # closes that off.
        if not data.order_items:
            raise OrderError("Order must contain at least one item")

        menu_item_ids = [item.menu_item_id for item in data.order_items]
        menu_items = {
            mi.id: mi
            for mi in self.session.exec(select(MenuItem).where(MenuItem.id.in_(menu_item_ids))).all()
        }

        subtotal = Decimal("0.00")
        line_items: List[tuple[OrderItemCreate, Decimal]] = []
        for item in data.order_items:
            menu_item = menu_items.get(item.menu_item_id)
            if not menu_item or menu_item.restaurant_id != data.restaurant_id or not menu_item.is_available:
                raise OrderError(f"Menu item {item.menu_item_id} is not available at this restaurant")
            line_total = menu_item.price * item.quantity
            subtotal += line_total
            line_items.append((item, menu_item.price))

        db_order = Order(
            customer_name=data.customer_name,
            customer_phone=data.customer_phone,
            status=data.status,
            special_instructions=data.special_instructions,
            restaurant_id=data.restaurant_id,
            user_id=data.user_id,
            session_id=data.session_id,
            subtotal=subtotal,
            tax=Decimal("0.00"),
            total_amount=subtotal,
        )
        db_order = self.orders.add(db_order)

        for item, unit_price in line_items:
            self.orders.add_order_item(
                OrderItem(
                    order_id=db_order.id,
                    menu_item_id=item.menu_item_id,
                    quantity=item.quantity,
                    unit_price=unit_price,
                    special_request=item.special_request,
                )
            )
        self.orders.commit()
        self.session.refresh(db_order)

        return db_order

    def get_order(self, order_id: UUID) -> Optional[Order]:
        return self.orders.get(order_id)

    def list_for_user(self, user_id: UUID) -> List[Order]:
        return self.orders.list_by_user(user_id)

    def list_for_restaurant(self, restaurant_id: UUID, limit: int = 50) -> List[Order]:
        return self.orders.list_by_restaurant(restaurant_id, limit)

    def update_status(self, order_id: UUID, status: str) -> Optional[Order]:
        order = self.orders.get(order_id)
        if order:
            order.status = status
            order.updated_at = datetime.utcnow()
            self.orders.add(order)
        return order

    def restaurant_analytics(self, restaurant_id: UUID) -> dict:
        orders = self.orders.list_by_restaurant(restaurant_id, limit=200)
        total_revenue = sum((o.total_amount for o in orders), Decimal("0.00"))
        delivered = [o for o in orders if o.status == "delivered"]
        pending = [o for o in orders if o.status in ("pending", "confirmed", "preparing")]
        return {
            "total_revenue": total_revenue,
            "total_orders": len(orders),
            "delivered_orders": len(delivered),
            "pending_orders": len(pending),
            "avg_order_value": total_revenue / len(orders) if orders else Decimal("0.00"),
        }
