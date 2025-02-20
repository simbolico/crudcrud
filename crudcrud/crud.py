# crudcrud/crud.py
from typing import Any, List, Dict, Generic, TypeVar, Type, Optional

from fastapi import HTTPException
from sqlmodel import SQLModel, Session, select
from sqlalchemy.engine import Engine
from .exceptions import ItemNotFoundException, CrudException

T = TypeVar("T", bound=SQLModel)


class SQLCRUD(Generic[T]):
    def __init__(self, model: Type[T], engine: Optional[Engine] = None) -> None:
        self.model = model
        self._pk: str = list(model.__table__.primary_key.columns.keys())[0]
        self.engine = engine

    def _get_session(self) -> Session:
        if self.engine is None:
            raise ValueError(
                "Engine must be provided during class instanciation (e.g. my_crud = SQLCRUD(MyModel, engine=my_engine)) or set explicitly (e.g. my_crud.engine = my_engine)."
            )
        return Session(self.engine)

    def get_all(self, skip: int = 0, limit: int = 100, session: Optional[Session] = None) -> List[T]:
        session = session or self._get_session()
        with session:
            stmt = select(self.model).offset(skip).limit(limit)
            return session.exec(stmt).all()

    def get(self, item_id: Any, session: Optional[Session] = None) -> T:
        session = session or self._get_session()
        with session:
            stmt = select(self.model).where(getattr(self.model, self._pk) == item_id)
            instance = session.exec(stmt).first()
            if not instance:
                raise ItemNotFoundException(f"Item with id {item_id} not found")  # Use custom exception
            return instance

    def create(self, item: Dict[str, Any], session: Optional[Session] = None) -> T:
        session = session or self._get_session()
        with session:
            instance = self.model(**item)
            session.add(instance)
            try:
                session.commit()
                session.refresh(instance)
                return instance
            except Exception as e:
                session.rollback()
                raise CrudException(f"Error creating item: {e}") from e # Use custom exception + preserve cause

    def update(self, item_id: Any, item: Dict[str, Any], session: Optional[Session] = None) -> T:
        session = session or self._get_session()
        with session:
            stmt = select(self.model).where(getattr(self.model, self._pk) == item_id)
            instance = session.exec(stmt).first()
            if not instance:
                raise ItemNotFoundException(f"Item with id {item_id} not found")

            for key, value in item.items():
                setattr(instance, key, value)
            try:
                session.add(instance)
                session.commit()
                session.refresh(instance)
                return instance
            except Exception as e:
                session.rollback()
                raise CrudException(f"Error updating item: {e}") from e

    def delete_all(self, session: Optional[Session] = None) -> List[T]:
        session = session or self._get_session()
        with session:
            stmt = select(self.model)
            instances = session.exec(stmt).all()
            for instance in instances:
                session.delete(instance)
            session.commit()
            return []  #  return an empty list

    def delete(self, item_id: Any, session: Optional[Session] = None) -> T:
        session = session or self._get_session()
        with session:
            stmt = select(self.model).where(getattr(self.model, self._pk) == item_id)
            instance = session.exec(stmt).first()
            if not instance:
                raise ItemNotFoundException(f"Item with id {item_id} not found")
            session.delete(instance)
            session.commit()
            return instance