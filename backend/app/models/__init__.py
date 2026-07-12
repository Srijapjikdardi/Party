"""
SQLModel table models, one domain per file.

This module must import every table model so SQLAlchemy's mapper
registry can resolve the string-based `Relationship(back_populates=...)`
references between them (e.g. Order <-> User), regardless of which file
each class lives in.
"""
from app.models.user import User
from app.models.restaurant import Restaurant
from app.models.table import Table
from app.models.menu_item import MenuItem
from app.models.dining_session import DiningSession
from app.models.session_participant import SessionParticipant
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.wallet import WalletTransaction
from app.models.notification import Notification

__all__ = [
    "User",
    "Restaurant",
    "Table",
    "MenuItem",
    "DiningSession",
    "SessionParticipant",
    "Order",
    "OrderItem",
    "WalletTransaction",
    "Notification",
]
