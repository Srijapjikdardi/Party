"""
Service layer: application/business logic. Routes call services;
services call repositories. Keeping this boundary means route handlers
stay thin (validate input, call a service, shape the response) and
business rules live in one testable place instead of being duplicated
across endpoints.
"""
from app.services.auth_service import AuthService, AuthError
from app.services.restaurant_service import RestaurantService
from app.services.menu_service import MenuService
from app.services.table_service import TableService
from app.services.session_service import DiningSessionService
from app.services.order_service import OrderService
from app.services.wallet_service import WalletService, WalletError
from app.services.notification_service import NotificationService

__all__ = [
    "AuthService", "AuthError",
    "RestaurantService",
    "MenuService",
    "TableService",
    "DiningSessionService",
    "OrderService",
    "WalletService", "WalletError",
    "NotificationService",
]
