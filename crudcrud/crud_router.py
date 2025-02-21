# crudcrud/router.py
from typing import Any, List, Optional, Generator, Type, TypeVar, Callable
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import SQLModel, Session, select
from sqlalchemy.engine import Engine

from .crud import SQLModelCRUD  # Import from the same package
from .exceptions import ItemNotFoundException  # Import custom exception

T = TypeVar("T", bound=SQLModel)

class SQLModelCRUDRouter(APIRouter):
    def __init__(
        self,
        model: Type[T],
        get_session: Callable[[], Generator[Session, None, None]],
        prefix: Optional[str] = None,
        tags: Optional[List[str]] = None,
        paginate: Optional[int] = None,
        get_crud: Optional[Callable[[Type[T]], SQLModelCRUD[T]]] = None,
        **kwargs: Any,
    ) -> None:
        self.model: Type[T] = model
        self.get_session = get_session
        self._pk: str = list(model.__table__.primary_key.columns.keys())[0]
        self.paginate_limit = paginate
        prefix = prefix or f"/{model.__tablename__}"
        tags = tags or [model.__tablename__.capitalize()]
        super().__init__(prefix=prefix, tags=tags, **kwargs)

        self.crud: SQLModelCRUD[T] = get_crud(model) if get_crud else None

        if self.crud is None:
            # This logic should never be reached if from_engine is used correctly.
            # Raising an exception is better than silently failing.
            raise ValueError("get_crud must be provided if not using from_engine")

        async def get_all_endpoint(
            skip: int = 0, limit: Optional[int] = None, session: Session = Depends(self.get_session)
        ):
            limit = limit or self.paginate_limit
            return self.crud.get_all(skip, limit, session)

        async def get_one_endpoint(item_id: Any, session: Session = Depends(self.get_session)):
            try:
                return self.crud.get(item_id, session)
            except ItemNotFoundException as e:
                raise HTTPException(status_code=404, detail=str(e)) from e

        async def create_endpoint(item: dict = Body(...), session: Session = Depends(self.get_session)):
            try:
                return self.crud.create(item, session)
            except Exception as e:
                # Catch *all* exceptions from crud and re-raise as HTTPException
                raise HTTPException(status_code=422, detail=str(e)) from e

        async def update_endpoint(
            item_id: Any, item: dict = Body(...), session: Session = Depends(self.get_session)
        ):
            try:
                return self.crud.update(item_id, item, session)
            except ItemNotFoundException as e:
                raise HTTPException(status_code=404, detail=str(e)) from e
            except Exception as e:
                raise HTTPException(status_code=422, detail=str(e)) from e

        async def delete_all_endpoint(session: Session = Depends(self.get_session)):
            try:
                return self.crud.delete_all(session)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e)) from e

        async def delete_one_endpoint(item_id: Any, session: Session = Depends(self.get_session)):
            try:
                return self.crud.delete(item_id, session)
            except ItemNotFoundException as e:
                 raise HTTPException(status_code=404, detail=str(e)) from e

        self.add_api_route("", get_all_endpoint, methods=["GET"], response_model=List[model])
        self.add_api_route("", create_endpoint, methods=["POST"], response_model=model)
        self.add_api_route("", delete_all_endpoint, methods=["DELETE"], response_model=List[model])
        self.add_api_route("/{item_id}", get_one_endpoint, methods=["GET"], response_model=model)
        self.add_api_route("/{item_id}", update_endpoint, methods=["PUT"], response_model=model)
        self.add_api_route("/{item_id}", delete_one_endpoint, methods=["DELETE"], response_model=model)

    @classmethod
    def from_engine(
        cls,
        model: Type[T],
        engine: Engine,
        prefix: Optional[str] = None,
        tags: Optional[List[str]] = None,
        paginate: Optional[int] = None,
        **kwargs: Any,
    ) -> "SQLModelCRUDRouter":
        """
        Create a CRUD router from an SQLAlchemy engine, using SQLModelCRUD.
        """
        crud = SQLModelCRUD(model, engine=engine)
        def get_session() -> Generator[Session, None, None]:
            with Session(engine) as session:
                yield session

        return cls(model, get_session, prefix=prefix, tags=tags, paginate=paginate, get_crud=lambda m: crud, **kwargs)