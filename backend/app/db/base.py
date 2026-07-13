"""
Shared declarative building blocks: a naming convention for constraints
(so Alembic autogenerate produces stable, predictable names instead of
SQLAlchemy's default auto-generated names) and mixins used across models.

- `UUIDPKMixin` — for entities referenced externally (URLs, QR codes,
  receipts, gateway webhooks): unguessable, safe to expose, safe to
  generate client-side before an INSERT round-trip.
- `IntPKMixin` — for high-volume internal child/join/log rows never
  referenced outside the DB (order items, cart items, staff links,
  transactions). Sequential ints are smaller and cheaper to index than
  UUIDs, which matters on Neon's free-tier storage cap.
- `TimestampMixin` — created_at/updated_at on every table.
- `SoftDeleteMixin` — deleted_at, applied only to entities with
  external references that must survive deletion for financial/audit
  history (User, Restaurant, MenuItem). See docs/DATABASE.md.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, ForeignKey, Integer, MetaData
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import Field, SQLModel

# Explicit naming convention: Alembic autogenerate needs this to produce
# deterministic constraint/index names across runs (otherwise every
# `alembic revision --autogenerate` diffs unrelated constraint renames).
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=NAMING_CONVENTION)
SQLModel.metadata = metadata


class UUIDPKMixin(SQLModel):
    # sa_type (not sa_column=Column(...)) so each subclass gets its own
    # Column instance — sa_column=Column(...) builds ONE Column object
    # when this mixin class body runs, and every table subclassing it
    # would try to attach that same object, which SQLAlchemy rejects
    # ("Column object 'id' already assigned to Table ...").
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, sa_type=PGUUID(as_uuid=True))


class IntPKMixin(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)


class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        nullable=False,
    )


class SoftDeleteMixin(SQLModel):
    deleted_at: Optional[datetime] = Field(default=None, index=True)


def uuid_fk(
    target: str,
    ondelete: str,
    *,
    nullable: bool = False,
    index: bool = True,
    primary_key: bool = False,
    unique: bool = False,
):
    """
    UUID foreign-key column with an explicit ON DELETE rule.
    `target` is "table.column", e.g. "restaurants.id".
    sqlmodel 0.0.14's Field(foreign_key=...) has no `ondelete` kwarg, so
    this builds the column directly via sa_column instead.
    """
    return Field(
        default=None if nullable else ...,
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey(target, ondelete=ondelete),
            nullable=nullable,
            index=index,
            primary_key=primary_key,
            unique=unique,
        ),
    )


def int_fk(target: str, ondelete: str, *, nullable: bool = False, index: bool = True):
    """Integer foreign-key column with an explicit ON DELETE rule."""
    return Field(
        default=None if nullable else ...,
        sa_column=Column(
            Integer,
            ForeignKey(target, ondelete=ondelete),
            nullable=nullable,
            index=index,
        ),
    )
