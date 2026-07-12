"""
Repository pattern: one class per aggregate, wrapping all direct
database session access for that entity. Services depend on
repositories, never on `sqlmodel.Session` or `select()` directly.
"""
from app.repositories.user_repository import UserRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.repositories.table_repository import TableRepository
from app.repositories.menu_repository import MenuRepository
from app.repositories.dining_session_repository import DiningSessionRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.wallet_repository import WalletRepository
from app.repositories.notification_repository import NotificationRepository

__all__ = [
    "UserRepository",
    "RestaurantRepository",
    "TableRepository",
    "MenuRepository",
    "DiningSessionRepository",
    "OrderRepository",
    "WalletRepository",
    "NotificationRepository",
]
