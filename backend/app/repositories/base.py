"""
Generic repository base class.

Concrete repositories subclass this for the common get-by-id / add /
commit plumbing, then add entity-specific query methods of their own.
This keeps raw `session.exec(select(...))` calls out of the service and
API layers — only repositories talk to the database session directly.
"""
from typing import Generic, Optional, Type, TypeVar

from sqlmodel import Session, SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    model: Type[ModelType]

    def __init__(self, session: Session):
        self.session = session

    def get(self, id: int) -> Optional[ModelType]:
        return self.session.get(self.model, id)

    def add(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def commit(self) -> None:
        self.session.commit()
