from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.db.base import SoftDeleteMixin, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.wallet import WalletTransaction
    from app.models.notification import Notification
    from app.models.session_participant import SessionParticipant
    from app.models.restaurant_staff import RestaurantStaff
    from app.models.cart import Cart
    from app.models.refresh_token import RefreshToken
    from app.models.payment import Payment
    from app.models.email_verification_token import EmailVerificationToken
    from app.models.password_reset_token import PasswordResetToken


class User(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, SQLModel, table=True):
    __tablename__ = "users"

    name: str
    email: str = Field(unique=True, index=True)
    phone: str = Field(unique=True, index=True)
    google_id: Optional[str] = Field(default=None, unique=True, index=True)
    apple_id: Optional[str] = Field(default=None, unique=True, index=True)
    password_hash: str
    # Platform-level UX hint only (drives which app shell the legacy SPA
    # shows on login: diner | merchant | waiter). NOT the authorization
    # source of truth for restaurant-scoped actions — that's
    # RestaurantStaff.role_id, checked per-restaurant. Keeping this
    # avoids breaking the existing signup/signin flow while
    # RestaurantStaff supplies the real, normalized permission model.
    role: str = Field(default="diner")
    is_admin: bool = Field(default=False)
    avatar_url: Optional[str] = None
    wallet_balance: Decimal = Field(default=Decimal("0.00"), max_digits=10, decimal_places=2)
    is_active: bool = Field(default=True)
    is_email_verified: bool = Field(default=False)
    # Brute-force lockout: incremented on each failed login, reset to 0
    # on success. locked_until is set (now + settings.account_lockout_minutes)
    # once failed_login_attempts hits settings.max_failed_login_attempts.
    # DB-backed rather than an in-memory counter so it survives restarts
    # and works correctly with more than one app instance.
    failed_login_attempts: int = Field(default=0)
    locked_until: Optional[datetime] = None

    orders: List["Order"] = Relationship(back_populates="user")
    wallet_transactions: List["WalletTransaction"] = Relationship(back_populates="user")
    notifications: List["Notification"] = Relationship(back_populates="user")
    session_participants: List["SessionParticipant"] = Relationship(back_populates="user")
    staff_memberships: List["RestaurantStaff"] = Relationship(back_populates="user")
    carts: List["Cart"] = Relationship(back_populates="user")
    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="user")
    payments: List["Payment"] = Relationship(back_populates="user")
    email_verification_tokens: List["EmailVerificationToken"] = Relationship(back_populates="user")
    password_reset_tokens: List["PasswordResetToken"] = Relationship(back_populates="user")
