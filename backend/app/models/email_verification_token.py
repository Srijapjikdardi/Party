"""
Email verification tokens. Same shape/precedent as RefreshToken
(app/models/refresh_token.py): only a hash is ever stored, never the
raw token — the raw value exists only in the emailed link and briefly
in memory while being hashed. No separate `updated_at`: `used_at` is
the only mutation this row ever gets, so a second timestamp column
would just duplicate it (same precedent as RefreshToken's
issued_at/revoked_at, no updated_at either).
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlmodel import Field, Index, Relationship, SQLModel

from app.db.base import IntPKMixin, uuid_fk

if TYPE_CHECKING:
    from app.models.user import User


class EmailVerificationToken(IntPKMixin, SQLModel, table=True):
    __tablename__ = "email_verification_tokens"
    __table_args__ = (
        Index("ix_email_verification_tokens_user_used", "user_id", "used_at"),
    )

    user_id: UUID = uuid_fk("users.id", ondelete="CASCADE", index=False)
    token_hash: str = Field(unique=True, index=True)
    expires_at: datetime
    used_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="email_verification_tokens")
