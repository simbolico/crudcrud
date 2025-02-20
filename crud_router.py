from typing import Any, List, Optional, Generator, Type, TypeVar, Callable
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import SQLModel, Session, select
from sqlalchemy.engine import Engine

T = TypeVar("T", bound=SQLModel)

class SQLModelCRUDRouter(APIRouter):
    def __init__(
        self,
        model: Type[T],
        get_session: Callable[[], Generator[Session, None, None]],
        prefix: Optional[str] = None,
        tags: Optional[List[str]] = None,
        paginate: Optional[int] = None,
        **kwargs: Any
    ) -> None:
        self.model: Type[T] = model
        self.get_session = get_session
        self._pk: str = list(model.__table__.primary_key.columns.keys())[0]
        self.paginate_limit = paginate
        prefix = prefix or f"/{model.__tablename__}"
        tags = tags or [model.__tablename__.capitalize()]
        super().__init__(prefix=prefix, tags=tags, **kwargs)

        # Define endpoints as closures to capture self properly.
        async def get_all_endpoint(skip: int = 0, limit: Optional[int] = None, session: Session = Depends(self.get_session)):
            return await self.get_all(skip, limit, session)

        async def get_one_endpoint(item_id: Any, session: Session = Depends(self.get_session)):
            return await self.get_one(item_id, session)

        async def create_endpoint(item: dict = Body(...), session: Session = Depends(self.get_session)):
            return await self.create(item, session)

        async def update_endpoint(item_id: Any, item: dict = Body(...), session: Session = Depends(self.get_session)):
            return await self.update(item_id, item, session)

        async def delete_all_endpoint(session: Session = Depends(self.get_session)):
            return await self.delete_all(session)

        async def delete_one_endpoint(item_id: Any, session: Session = Depends(self.get_session)):
            return await self.delete_one(item_id, session)

        self.add_api_route("", get_all_endpoint, methods=["GET"], response_model=List[model])
        self.add_api_route("", create_endpoint, methods=["POST"], response_model=model)
        self.add_api_route("", delete_all_endpoint, methods=["DELETE"], response_model=List[model])
        self.add_api_route("/{item_id}", get_one_endpoint, methods=["GET"], response_model=model)
        self.add_api_route("/{item_id}", update_endpoint, methods=["PUT"], response_model=model)
        self.add_api_route("/{item_id}", delete_one_endpoint, methods=["DELETE"], response_model=model)

    async def get_all(self, skip: int = 0, limit: Optional[int] = None, session: Session = None) -> List[T]:
        lmt = limit or self.paginate_limit
        stmt = select(self.model).offset(skip)
        if lmt:
            stmt = stmt.limit(lmt)
        return session.exec(stmt).all()

    async def get_one(self, item_id: Any, session: Session = None) -> T:
        stmt = select(self.model).where(getattr(self.model, self._pk) == item_id)
        instance = session.exec(stmt).first()
        if not instance:
            raise HTTPException(status_code=404, detail="Item not found")
        return instance

    async def create(self, item: dict, session: Session = None) -> T:
        instance = self.model(**item)
        session.add(instance)
        try:
            session.commit()
            session.refresh(instance)
            return instance
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=422, detail=str(e))

    async def update(self, item_id: Any, item: dict, session: Session = None) -> T:
        stmt = select(self.model).where(getattr(self.model, self._pk) == item_id)
        instance = session.exec(stmt).first()
        if not instance:
            raise HTTPException(status_code=404, detail="Item not found")
        for key, value in item.items():
            setattr(instance, key, value)
        try:
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=422, detail=str(e))

    async def delete_all(self, session: Session = None) -> List[T]:
        stmt = select(self.model)
        instances = session.exec(stmt).all()
        for instance in instances:
            session.delete(instance)
        session.commit()
        return []

    async def delete_one(self, item_id: Any, session: Session = None) -> T:
        stmt = select(self.model).where(getattr(self.model, self._pk) == item_id)
        instance = session.exec(stmt).first()
        if not instance:
            raise HTTPException(status_code=404, detail="Item not found")
        session.delete(instance)
        session.commit()
        return instance

    @classmethod
    def from_engine(
        cls,
        model: Type[T],
        engine: Engine,
        prefix: Optional[str] = None,
        tags: Optional[List[str]] = None,
        paginate: Optional[int] = None,
        **kwargs: Any
    ) -> "SQLModelCRUDRouter":
        """
        Create a CRUD router from an SQLAlchemy engine. This method creates a session dependency internally.
        """
        def get_session() -> Generator[Session, None, None]:
            with Session(engine) as session:
                yield session

        return cls(model, get_session, prefix=prefix, tags=tags, paginate=paginate, **kwargs)
