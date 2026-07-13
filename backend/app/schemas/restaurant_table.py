from uuid import UUID

from sqlmodel import SQLModel


class TableRead(SQLModel):
    id: UUID
    restaurant_id: UUID
    number: str
    capacity: int
    status: str
    qr_code_token: str

    class Config:
        from_attributes = True
