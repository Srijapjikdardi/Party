"""
SQLModel table models, one domain per file. This module imports every
table model so SQLAlchemy's mapper registry can resolve the string-based
`Relationship(back_populates=...)` references between them, regardless
of which file each class lives in.
"""
from app.models.restaurant_role import RestaurantRole
from app.models.user import User
from app.models.restaurant import Restaurant
from app.models.restaurant_staff import RestaurantStaff
from app.models.restaurant_table import RestaurantTable
from app.models.menu_category import MenuCategory
from app.models.menu_item import MenuItem
from app.models.dining_session import DiningSession
from app.models.session_participant import SessionParticipant
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.bill import Bill
from app.models.bill_split_record import BillSplitRecord
from app.models.payment import Payment
from app.models.payment_transaction import PaymentTransaction
from app.models.refresh_token import RefreshToken
from app.models.wallet import WalletTransaction
from app.models.notification import Notification

__all__ = [
    "RestaurantRole",
    "User",
    "Restaurant",
    "RestaurantStaff",
    "RestaurantTable",
    "MenuCategory",
    "MenuItem",
    "DiningSession",
    "SessionParticipant",
    "Cart",
    "CartItem",
    "Order",
    "OrderItem",
    "Bill",
    "BillSplitRecord",
    "Payment",
    "PaymentTransaction",
    "RefreshToken",
    "WalletTransaction",
    "Notification",
]
