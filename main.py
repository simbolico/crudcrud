from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from sqlmodel import SQLModel, Field, create_engine
from crud_router import SQLModelCRUDRouter

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=False)

# Define database models
class ItemCreate(SQLModel):
    name: str
    description: str | None = None

class Item(ItemCreate, table=True):
    id: int | None = Field(default=None, primary_key=True)

class Object(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    value: float

# Create database tables
SQLModel.metadata.create_all(engine)

app = FastAPI()

# Use the class method to create routers without the user having to define the session dependency.
item_router = SQLModelCRUDRouter.from_engine(model=Item, engine=engine, paginate=10)
app.include_router(item_router)

object_router = SQLModelCRUDRouter.from_engine(model=Object, engine=engine, paginate=10)
app.include_router(object_router)

@app.get("/", include_in_schema=False)
async def custom_swagger_ui_html():
    return RedirectResponse(url="/docs")
