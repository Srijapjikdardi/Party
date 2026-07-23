"""
Repository pattern: one class per aggregate, wrapping all direct
database session access for that entity. Services depend on
repositories, never on `sqlmodel.Session` or `select()` directly.
"""
from app.repositories.bill_repository import BillRepository
from app.repositories.bill_split_record_repository import BillSplitRecordRepository
from app.repositories.dining_session_repository import DiningSessionRepository
from app.repositories.email_verification_token_repository import EmailVerificationTokenRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.menu_repository import MenuRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.repositories.session_participant_repository import SessionParticipantRepository
from app.repositories.table_repository import TableRepository
from app.repositories.user_repository import UserRepository
from app.repositories.wallet_repository import WalletRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.password_reset_token_repository import PasswordResetTokenRepository

__all__ = [
    "BillRepository",
    "BillSplitRecordRepository",
    "DiningSessionRepository",
    "OrderRepository",
    "MenuRepository",
    "RestaurantRepository",
    "TableRepository",
    "UserRepository",
    "WalletRepository",
    "NotificationRepository",
    "RefreshTokenRepository",
    "SessionParticipantRepository",
    "EmailVerificationTokenRepository",
    "PasswordResetTokenRepository",
]