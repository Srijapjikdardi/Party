"""
Persistent refresh tokens. The M2 access-token store is still an
in-memory dict (see app/core/security.py) — deliberately out of scope
for this milestone (database layer only; see docs/MIGRATION_PLAN.md's
"explicitly out of scope" note). This table gives the future JWT
migration somewhere to land without another schema change: only the
token *hash* is stored, never the raw token, and `revoked_at` supports
"log out everywhere".
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlmodel import Field, Index, Relationship, SQLModel

from app.db.base import IntPKMixin, uuid_fk

if TYPE_CHECKING:
    from app.models.user import User


class RefreshToken(IntPKMixin, SQLModel, table=True):
    __tablename__ = "refresh_tokens"
    __table_args__ = (
        Index("ix_refresh_tokens_user_revoked", "user_id", "revoked_at"),
    )

    user_id: UUID = uuid_fk("users.id", ondelete="CASCADE", index=False)
    token_hash: str = Field(unique=True, index=True)
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    revoked_at: Optional[datetime] = None

    user: "User" = Relationship(back_populates="refresh_tokens")
