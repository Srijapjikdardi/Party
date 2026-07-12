from typing import Optional

from sqlmodel import Session

from app.core.security import create_token, hash_password, revoke_token, verify_password
from app.models import Notification, User
from app.repositories import NotificationRepository, UserRepository
from app.schemas import UserCreate, UserLogin


class AuthError(Exception):
    """Raised for auth failures the API layer should turn into 4xx responses."""


class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.users = UserRepository(session)
        self.notifications = NotificationRepository(session)

    def signup(self, data: UserCreate) -> tuple[str, User]:
        if self.users.get_by_email(data.email):
            raise AuthError("Email already registered")

        user = User(
            name=data.name,
            email=data.email,
            phone=data.phone,
            password_hash=hash_password(data.password),
            role=data.role,
            wallet_balance=500.0,  # Welcome bonus
        )
        user = self.users.add(user)

        welcome = Notification(
            user_id=user.id,
            title="Welcome to PartyPe! 🎉",
            body="Your account is ready. You have ₹500 in your wallet to get started.",
            icon="celebration",
        )
        self.notifications.add(welcome)

        return create_token(user.id), user

    def signin(self, creds: UserLogin) -> tuple[str, User]:
        user = self.users.get_by_email(creds.email)
        if not user or not verify_password(creds.password, user.password_hash):
            raise AuthError("Invalid credentials")
        return create_token(user.id), user

    def signout(self, token: str) -> None:
        revoke_token(token)

    def get_user(self, user_id: int) -> Optional[User]:
        return self.users.get(user_id)
