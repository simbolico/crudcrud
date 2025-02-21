from sqlalchemy.pool import StaticPool
import pytest
from sqlmodel import SQLModel, create_engine, Session, Field

class TestItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

@pytest.fixture(scope="session")
def engine():
    eng = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(eng)
    return eng

@pytest.fixture
def session(engine):
    with Session(engine) as s:
        yield s

@pytest.fixture
def test_model():
    return TestItem

@pytest.fixture
def app(engine, test_model):
    from fastapi import FastAPI
    from crudcrud import SQLModelCRUDRouter
    app = FastAPI()
    SQLModel.metadata.create_all(engine)
    router = SQLModelCRUDRouter.from_engine(model=test_model, engine=engine, paginate=10)
    app.include_router(router)
    return app

@pytest.fixture
def client(app):
    from fastapi.testclient import TestClient
    return TestClient(app)
