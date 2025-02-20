# main.py
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from sqlmodel import SQLModel, Field, create_engine
from crudcrud import SQLModelCRUDRouter  # Import from installed package
# from crud import SQLCRUD  # Now we DON'T use SQLCRUD directly in main.py

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=False)

class ItemCreate(SQLModel):
    name: str
    description: str | None = None

class Item(ItemCreate, table=True):
    id: int | None = Field(default=None, primary_key=True)

class Object(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    value: float

SQLModel.metadata.create_all(engine)

app = FastAPI()

# ---  Using SQLModelCRUDRouter.from_engine ---
item_router = SQLModelCRUDRouter.from_engine(model=Item, engine=engine, paginate=10)
app.include_router(item_router)

object_router = SQLModelCRUDRouter.from_engine(model=Object, engine=engine, paginate=10)
app.include_router(object_router)

@app.get("/", include_in_schema=False)
async def custom_swagger_ui_html():
    return RedirectResponse(url="/docs")