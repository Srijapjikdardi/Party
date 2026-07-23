from decimal import Decimal
from uuid import UUID

from sqlmodel import SQLModel


class PaymentCreate(SQLModel):
    amount: Decimal


class PaymentRead(SQLModel):
    id: int
    amount: Decimal
    # other fields as needed