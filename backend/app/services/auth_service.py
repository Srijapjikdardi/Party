"""
Authentication: register, login, logout, refresh (with rotation +
reuse detection), email verification, password reset. See
docs/AUTHENTICATION.md for the full flow and rationale.
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlmodel import Session

from app.core.audit import log_auth_event
from app.core.config import settings
from app.core.email import email_service
from app.core.errors import AppError
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models import EmailVerificationToken, Notification, PasswordResetToken, RefreshToken, User
from app.repositories import (
    EmailVerificationTokenRepository,
    NotificationRepository,
    PasswordResetTokenRepository,
    RefreshTokenRepository,
    UserRepository,
)
from app.schemas import RegisterRequest, TokenPairResponse
from app.schemas.auth import LoginRequest


class AuthError(AppError):
    """Raised for auth failures — the registered AppError handler
    (app/core/errors.py) turns this into a consistent JSON error
    response automatically; endpoints don't need to catch it."""

    def __init__(self, message: str, status_code: int = 401):
        super().__init__(status_code, "auth_error", message)


class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.users = UserRepository(session)
        self.notifications = NotificationRepository(session)
        self.refresh_tokens = RefreshTokenRepository(session)
        self.email_tokens = EmailVerificationTokenRepository(session)
        self.reset_tokens = PasswordResetTokenRepository(session)

    # ── Token issuance ───────────────────────────────────

    def _issue_token_pair(self, user: User) -> TokenPairResponse:
        access_token = create_access_token(user.id, user.role)
        raw_refresh = generate_refresh_token()
        self.refresh_tokens.add(
            RefreshToken(
                user_id=user.id,
                token_hash=hash_token(raw_refresh),
                expires_at=datetime.utcnow() + timedelta(days=settings.refresh_token_ttl_days),
            )
        )
        return TokenPairResponse(
            access_token=access_token,
            refresh_token=raw_refresh,
            expires_in=settings.access_token_ttl_minutes * 60,
            token=access_token,  # legacy SPA compatibility
        )

    # ── Register / login / logout ───────────────────────

    def register(self, data: RegisterRequest, ip: Optional[str] = None) -> tuple[TokenPairResponse, User]:
        if self.users.get_by_email_including_deleted(data.email):
            log_auth_event("register", success=False, email=data.email, ip=ip, detail="email already registered")
            raise AuthError("Email already registered", status_code=400)

        user = User(
            name=data.name,
            email=data.email,
            phone=data.phone,
            password_hash=hash_password(data.password),
            role=data.role,
            wallet_balance=Decimal("500.00"),  # Welcome bonus
        )
        user = self.users.add(user)

        self.notifications.add(Notification(
            user_id=user.id,
            title="Welcome to PartyPe! 🎉",
            body="Your account is ready. You have ₹500 in your wallet to get started.",
            icon="celebration",
        ))

        self._issue_email_verification(user)
        log_auth_event("register", success=True, user_id=user.id, email=user.email, ip=ip)
        return self._issue_token_pair(user), user

    def login(self, creds: LoginRequest, ip: Optional[str] = None) -> tuple[TokenPairResponse, User]:
        user = self.users.get_by_email(creds.email)
        if not user:
            log_auth_event("login", success=False, email=creds.email, ip=ip, detail="no such user")
            raise AuthError("Invalid credentials")

        if user.locked_until and user.locked_until > datetime.utcnow():
            log_auth_event("login", success=False, user_id=user.id, email=user.email, ip=ip, detail="account locked")
            raise AuthError(
                f"Account temporarily locked due to repeated failed logins. "
                f"Try again after {user.locked_until.isoformat()}.",
                status_code=423,
            )

        if not user.is_active:
            log_auth_event("login", success=False, user_id=user.id, email=user.email, ip=ip, detail="deactivated")
            raise AuthError("Account is deactivated", status_code=403)

        if not verify_password(creds.password, user.password_hash):
            self._register_failed_login(user)
            log_auth_event("login", success=False, user_id=user.id, email=user.email, ip=ip, detail="bad password")
            raise AuthError("Invalid credentials")

        user.failed_login_attempts = 0
        user.locked_until = None
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        log_auth_event("login", success=True, user_id=user.id, email=user.email, ip=ip)
        return self._issue_token_pair(user), user

    def _register_failed_login(self, user: User) -> None:
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= settings.max_failed_login_attempts:
            user.locked_until = datetime.utcnow() + timedelta(minutes=settings.account_lockout_minutes)
        self.session.add(user)
        self.session.commit()

    def logout(self, raw_refresh_token: str, ip: Optional[str] = None) -> None:
        token = self.refresh_tokens.get_by_hash(hash_token(raw_refresh_token))
        if token and not token.revoked_at:
            self.refresh_tokens.revoke(token)
            log_auth_event("logout", success=True, user_id=token.user_id, ip=ip)

    # ── Refresh (rotation + reuse detection) ────────────

    def refresh(self, raw_refresh_token: str, ip: Optional[str] = None) -> TokenPairResponse:
        token = self.refresh_tokens.get_by_hash(hash_token(raw_refresh_token))
        if not token:
            log_auth_event("refresh", success=False, ip=ip, detail="unknown token")
            raise AuthError("Invalid refresh token")

        if token.revoked_at:
            # This token was already used once (rotation revokes on
            # use) or explicitly logged out — presenting it again means
            # it leaked. Revoke every active session for this user as
            # a precaution.
            self.refresh_tokens.revoke_all_for_user(token.user_id)
            log_auth_event(
                "refresh_reuse_detected", success=False, user_id=token.user_id, ip=ip,
                detail="revoked refresh token reused — all sessions revoked",
            )
            raise AuthError("Refresh token has been revoked")

        if token.expires_at < datetime.utcnow():
            log_auth_event("refresh", success=False, user_id=token.user_id, ip=ip, detail="expired token")
            raise AuthError("Refresh token has expired")

        user = self.users.get(token.user_id)
        if not user or not user.is_active:
            log_auth_event("refresh", success=False, user_id=token.user_id, ip=ip, detail="user inactive/missing")
            raise AuthError("Account is not available")

        self.refresh_tokens.revoke(token)  # rotation: old token is single-use
        log_auth_event("refresh", success=True, user_id=user.id, ip=ip)
        return self._issue_token_pair(user)

    # ── Email verification ──────────────────────────────

    def _issue_email_verification(self, user: User) -> None:
        self.email_tokens.invalidate_unused_for_user(user.id)
        raw = generate_refresh_token()
        self.email_tokens.add(EmailVerificationToken(
            user_id=user.id,
            token_hash=hash_token(raw),
            expires_at=datetime.utcnow() + timedelta(hours=settings.email_verification_ttl_hours),
        ))
        email_service.send_verification_email(user.email, raw)

    def verify_email(self, raw_token: str) -> None:
        token = self.email_tokens.get_by_hash(hash_token(raw_token))
        if not token or token.used_at or token.expires_at < datetime.utcnow():
            raise AuthError("Invalid or expired verification token", status_code=400)

        user = self.users.get(token.user_id)
        if not user:
            raise AuthError("Invalid or expired verification token", status_code=400)

        user.is_email_verified = True
        token.used_at = datetime.utcnow()
        self.session.add(user)
        self.session.add(token)
        self.session.commit()
        log_auth_event("verify_email", success=True, user_id=user.id, email=user.email)

    def resend_verification(self, email: str) -> None:
        user = self.users.get_by_email(email)
        if user and not user.is_email_verified:
            self._issue_email_verification(user)
        # Always the same outward result whether or not the email
        # exists / is already verified — see forgot_password for why.
        log_auth_event("resend_verification", success=True, email=email)

    # ── Password reset ───────────────────────────────────

    def forgot_password(self, email: str, ip: Optional[str] = None) -> None:
        user = self.users.get_by_email(email)
        if user:
            self.reset_tokens.invalidate_unused_for_user(user.id)
            raw = generate_refresh_token()
            self.reset_tokens.add(PasswordResetToken(
                user_id=user.id,
                token_hash=hash_token(raw),
                expires_at=datetime.utcnow() + timedelta(minutes=settings.password_reset_ttl_minutes),
            ))
            email_service.send_password_reset_email(user.email, raw)
        # Never reveal whether the email is registered — same response
        # either way, prevents account enumeration via this endpoint.
        log_auth_event("forgot_password", success=True, email=email, ip=ip)

    def reset_password(self, raw_token: str, new_password: str, ip: Optional[str] = None) -> None:
        token = self.reset_tokens.get_by_hash(hash_token(raw_token))
        if not token or token.used_at or token.expires_at < datetime.utcnow():
            log_auth_event("reset_password", success=False, ip=ip, detail="invalid/expired token")
            raise AuthError("Invalid or expired reset token", status_code=400)

        user = self.users.get(token.user_id)
        if not user:
            raise AuthError("Invalid or expired reset token", status_code=400)

        user.password_hash = hash_password(new_password)
        user.failed_login_attempts = 0
        user.locked_until = None
        token.used_at = datetime.utcnow()
        self.session.add(user)
        self.session.add(token)
        self.session.commit()

        # Force re-login everywhere — a password reset should invalidate
        # any session that might belong to whoever had the old password.
        self.refresh_tokens.revoke_all_for_user(user.id)
        log_auth_event("reset_password", success=True, user_id=user.id, ip=ip)

    def get_user(self, user_id: UUID) -> Optional[User]:
        return self.users.get(user_id)
