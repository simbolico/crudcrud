from typing import Any, List, Optional, Generator, Type, TypeVar
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Body
from fastapi.responses import RedirectResponse
from sqlmodel import SQLModel, Field, Session, create_engine, select

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=False)
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

T = TypeVar("T", bound=SQLModel)

class SQLModelCRUDRouter(APIRouter):
    def __init__(
        self,
        model: Type[T],
        get_session: Any,
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
        self.add_api_route("", self.get_all, methods=["GET"], response_model=List[model])
        self.add_api_route("", self.create, methods=["POST"], response_model=model)
        self.add_api_route("", self.delete_all, methods=["DELETE"], response_model=List[model])
        self.add_api_route("/{item_id}", self.get_one, methods=["GET"], response_model=model)
        self.add_api_route("/{item_id}", self.update, methods=["PUT"], response_model=model)
        self.add_api_route("/{item_id}", self.delete_one, methods=["DELETE"], response_model=model)

    async def get_all(
        self,
        skip: int = 0,
        limit: Optional[int] = None,
        session: Session = Depends(get_session)
    ) -> List[T]:
        lmt = limit or self.paginate_limit
        stmt = select(self.model).offset(skip)
        if lmt:
            stmt = stmt.limit(lmt)
        return session.exec(stmt).all()

    async def get_one(self, item_id: Any, session: Session = Depends(get_session)) -> T:
        stmt = select(self.model).where(getattr(self.model, self._pk) == item_id)
        instance = session.exec(stmt).first()
        if not instance:
            raise HTTPException(status_code=404, detail="Item not found")
        return instance

    async def create(self, item: dict = Body(...), session: Session = Depends(get_session)) -> T:
        instance = self.model(**item)
        session.add(instance)
        try:
            session.commit()
            session.refresh(instance)
            return instance
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=422, detail=str(e))

    async def update(self, item_id: Any, item: dict = Body(...), session: Session = Depends(get_session)) -> T:
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

    async def delete_all(self, session: Session = Depends(get_session)) -> List[T]:
        stmt = select(self.model)
        instances = session.exec(stmt).all()
        for instance in instances:
            session.delete(instance)
        session.commit()
        return []

    async def delete_one(self, item_id: Any, session: Session = Depends(get_session)) -> T:
        stmt = select(self.model).where(getattr(self.model, self._pk) == item_id)
        instance = session.exec(stmt).first()
        if not instance:
            raise HTTPException(status_code=404, detail="Item not found")
        session.delete(instance)
        session.commit()
        return instance

class ItemCreate(SQLModel):
    name: str
    description: Optional[str] = None

class Item(ItemCreate, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class Object(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    value: float

SQLModel.metadata.create_all(engine)
app = FastAPI()
item_router = SQLModelCRUDRouter(model=Item, get_session=get_session, paginate=10)
app.include_router(item_router)



object_router = SQLModelCRUDRouter(model=Object, get_session=get_session, paginate=10)
app.include_router(object_router)

# Set the default route to display the Swagger UI
@app.get("/", include_in_schema=False)
async def custom_swagger_ui_html():
    return RedirectResponse(url="/docs")