"""
User profile management: update profile, change password, deactivate,
delete. Distinct from AuthService (login/tokens) per the endpoint
grouping (/api/v1/users vs /api/v1/auth).
"""
from datetime import datetime

from sqlmodel import Session

from app.core.audit import log_auth_event
from app.core.errors import AppError
from app.core.security import hash_password, verify_password
from app.models import User
from app.repositories import RefreshTokenRepository, UserRepository
from app.schemas.auth import UpdateProfileRequest


class UserError(AppError):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(status_code, "user_error", message)


class UserService:
    def __init__(self, session: Session):
        self.session = session
        self.users = UserRepository(session)
        self.refresh_tokens = RefreshTokenRepository(session)

    def update_profile(self, user: User, data: UpdateProfileRequest) -> User:
        if data.name is not None:
            user.name = data.name
        if data.avatar_url is not None:
            user.avatar_url = data.avatar_url
        user.updated_at = datetime.utcnow()
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def change_password(self, user: User, current_password: str, new_password: str) -> None:
        if not verify_password(current_password, user.password_hash):
            raise UserError("Current password is incorrect")

        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.utcnow()
        self.session.add(user)
        self.session.commit()

        # Same rationale as AuthService.reset_password: a changed
        # password should kill every other session.
        self.refresh_tokens.revoke_all_for_user(user.id)
        log_auth_event("change_password", success=True, user_id=user.id, email=user.email)

    def deactivate(self, user: User) -> None:
        user.is_active = False
        user.updated_at = datetime.utcnow()
        self.session.add(user)
        self.session.commit()
        self.refresh_tokens.revoke_all_for_user(user.id)
        log_auth_event("deactivate", success=True, user_id=user.id, email=user.email)

    def delete_account(self, user: User) -> None:
        """Soft delete — justified because orders/staff/session-
        participant rows RESTRICT-reference user_id and must survive
        for financial/audit history (see docs/DATABASE.md). A hard
        delete would either violate those FKs or require cascading
        through a customer's entire order history, which is never
        what "delete my account" should silently do.
        """
        user.deleted_at = datetime.utcnow()
        user.is_active = False
        user.updated_at = datetime.utcnow()
        self.session.add(user)
        self.session.commit()
        self.refresh_tokens.revoke_all_for_user(user.id)
        log_auth_event("delete_account", success=True, user_id=user.id, email=user.email)
