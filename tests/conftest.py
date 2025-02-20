# tests/conftest.py
import pytest
from sqlmodel import SQLModel, create_engine, Session, Field
from typing import Generator

# Define a simple model for testing
class TestModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    value: float

@pytest.fixture(scope="session")
def engine():
    engine = create_engine("sqlite:///:memory:")  # Use in-memory SQLite for tests
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture(scope="function")
def session(engine) -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
        session.rollback()  # Rollback changes after each test

@pytest.fixture(scope="function")
def test_model():
    return TestModel