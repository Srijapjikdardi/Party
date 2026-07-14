"""
Auth request/response schemas. Password policy is enforced here (not
in the service layer) so a malformed password never reaches business
logic and the client gets one consistent 422 shape for every
password-accepting endpoint (register, reset, change).
"""
import re
from typing import Optional

from pydantic import EmailStr, field_validator
from sqlmodel import SQLModel

# Min 10 chars, at least one upper, one lower, one digit, one special
# char. Deliberately not requiring a specific special-char set beyond
# "not alphanumeric" — restrictive special-char allowlists reject
# legitimate passwords for no security benefit.
_PASSWORD_MIN_LENGTH = 10


def validate_password_strength(password: str) -> str:
    if len(password) < _PASSWORD_MIN_LENGTH:
        raise ValueError(f"Password must be at least {_PASSWORD_MIN_LENGTH} characters")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit")
    if not re.search(r"[^A-Za-z0-9]", password):
        raise ValueError("Password must contain at least one special character")
    return password


class RegisterRequest(SQLModel):
    name: str
    email: EmailStr
    phone: str
    password: str
    role: str = "diner"

    @field_validator("password")
    @classmethod
    def _check_password(cls, v: str) -> str:
        return validate_password_strength(v)


class LoginRequest(SQLModel):
    email: EmailStr
    password: str


class TokenPairResponse(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # access token TTL, seconds
    # Back-compat: frontend/legacy-spa/index.html reads `token` (the
    # bearer it sends as Authorization). See docs/AUTHENTICATION.md.
    token: str


class RefreshRequest(SQLModel):
    refresh_token: str


class LogoutRequest(SQLModel):
    refresh_token: str


class VerifyEmailRequest(SQLModel):
    token: str


class ResendVerificationRequest(SQLModel):
    email: EmailStr


class ForgotPasswordRequest(SQLModel):
    email: EmailStr


class ResetPasswordRequest(SQLModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def _check_password(cls, v: str) -> str:
        return validate_password_strength(v)


class ChangePasswordRequest(SQLModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def _check_password(cls, v: str) -> str:
        return validate_password_strength(v)


class UpdateProfileRequest(SQLModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class MessageResponse(SQLModel):
    message: str
