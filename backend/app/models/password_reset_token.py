"""
Password reset tokens. Same shape/rationale as EmailVerificationToken.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlmodel import Field, Index, Relationship, SQLModel

from app.db.base import IntPKMixin, uuid_fk

if TYPE_CHECKING:
    from app.models.user import User


class PasswordResetToken(IntPKMixin, SQLModel, table=True):
    __tablename__ = "password_reset_tokens"
    __table_args__ = (
        Index("ix_password_reset_tokens_user_used", "user_id", "used_at"),
    )

    user_id: UUID = uuid_fk("users.id", ondelete="CASCADE", index=False)
    token_hash: str = Field(unique=True, index=True)
    expires_at: datetime
    used_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="password_reset_tokens")
