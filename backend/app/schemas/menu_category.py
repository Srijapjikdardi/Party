from uuid import UUID

from sqlmodel import SQLModel


class MenuCategoryRead(SQLModel):
    id: int
    restaurant_id: UUID
    name: str
    display_order: int

    class Config:
        from_attributes = True
