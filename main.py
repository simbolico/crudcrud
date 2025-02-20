from typing import Optional, Generator
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from sqlmodel import SQLModel, Field, Session, create_engine
from crud_router import SQLModelCRUDRouter

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=False)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

# Define database models
class ItemCreate(SQLModel):
    name: str
    description: Optional[str] = None

class Item(ItemCreate, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class Object(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    value: float

# Create database tables
SQLModel.metadata.create_all(engine)

# Initialize FastAPI app
app = FastAPI()

# Register CRUD routers
item_router = SQLModelCRUDRouter(model=Item, get_session=get_session, paginate=10)
app.include_router(item_router)

object_router = SQLModelCRUDRouter(model=Object, get_session=get_session, paginate=10)
app.include_router(object_router)

# Set the default route to display the Swagger UI
@app.get("/", include_in_schema=False)
async def custom_swagger_ui_html():
    return RedirectResponse(url="/docs")
