from sqlmodel import SQLModel


class TableRead(SQLModel):
    id: int
    restaurant_id: int
    number: str
    capacity: int
    status: str

    class Config:
        from_attributes = True
