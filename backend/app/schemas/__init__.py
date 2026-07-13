"""
Pydantic-only request/response schemas, kept separate from the SQLModel
table models in `app.models`. A response shape can change without
touching the database schema, and vice versa.
"""
from app.schemas.user import UserCreate, UserRead, UserLogin
from app.schemas.restaurant import RestaurantBase, RestaurantCreate, RestaurantRead
from app.schemas.restaurant_table import TableRead
from app.schemas.menu_category import MenuCategoryRead
from app.schemas.menu_item import MenuItemBase, MenuItemCreate, MenuItemRead
from app.schemas.dining_session import DiningSessionCreate, DiningSessionRead
from app.schemas.session_participant import SessionParticipantRead
from app.schemas.order_item import OrderItemBase, OrderItemCreate, OrderItemRead
from app.schemas.order import OrderBase, OrderCreate, OrderRead, OrderStatusUpdate
from app.schemas.wallet import WalletTransactionRead, WalletTopup
from app.schemas.notification import NotificationRead

__all__ = [
    "UserCreate", "UserRead", "UserLogin",
    "RestaurantBase", "RestaurantCreate", "RestaurantRead",
    "TableRead",
    "MenuCategoryRead",
    "MenuItemBase", "MenuItemCreate", "MenuItemRead",
    "DiningSessionCreate", "DiningSessionRead",
    "SessionParticipantRead",
    "OrderItemBase", "OrderItemCreate", "OrderItemRead",
    "OrderBase", "OrderCreate", "OrderRead", "OrderStatusUpdate",
    "WalletTransactionRead", "WalletTopup",
    "NotificationRead",
]
