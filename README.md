# crudcrud

[![PyPI version](https://badge.fury.io/py/crudcrud.svg)](https://badge.fury.io/py/crudcrud)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://github.com/<your_username>/<your_repo_name>/actions/workflows/test.yml/badge.svg)](https://github.com/<your_username>/<your_repo_name>/actions/workflows/test.yml)  <!--  Replace with your actual GitHub Actions badge URL -->

`crudcrud` is a minimalist, yet powerful, Python library designed to streamline CRUD (Create, Read, Update, Delete) operations in FastAPI applications using SQLModel.  It aims for simplicity, excellent developer experience (DX), and a best-in-class onboarding experience.  It focuses on getting you up and running quickly, without sacrificing flexibility or control.

## Features

*   **Automatic API Route Generation:**  Instantly create RESTful API endpoints for your SQLModel models with `SQLModelCRUDRouter`.  No need to write repetitive boilerplate code for each CRUD operation.
*   **SQLModel Integration:** Seamlessly works with SQLModel, combining the power of SQLAlchemy and Pydantic for database models and data validation.
*   **Engine-Based Initialization:** The recommended approach is using the `.from_engine()` method, which automatically handles session management, reducing setup complexity.
*   **Customizable:** Easily override or extend the default behavior by providing your own session factory or CRUD logic.
*   **Built-in Error Handling:**  Handles common database errors gracefully, returning appropriate HTTP status codes and informative error messages.  Includes custom exceptions (`CrudException`, `ItemNotFoundException`) for fine-grained error control.
*   **Pagination Support:**  Built-in support for pagination, allowing you to efficiently handle large datasets.
*   **Type-Safe:**  Fully type-hinted for improved code clarity and maintainability.
*   **Test-Driven:**  Includes a comprehensive suite of unit tests, ensuring reliability and stability.
*  **Easy to learn**: a single file example is provided.

## Installation

```bash
pip install crudcrud
```

## Quick Start (Single File Example)

This example demonstrates how to create a complete FastAPI application with CRUD operations for an `Item` model in a *single* Python file.

```python
# app.py
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from sqlmodel import SQLModel, create_engine, Field
from crudcrud import SQLModelCRUDRouter

# --- Database Setup (In-Memory SQLite for Simplicity) ---
engine = create_engine("sqlite:///:memory:", echo=False)  # Use in-memory DB for this example

# --- Define your SQLModel ---
class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str | None = None

# --- Create the Database Tables ---
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# --- Create the FastAPI App ---
app = FastAPI()

# --- Create the CRUD Router ---
# Use .from_engine() for automatic session handling – the BEST way!
item_router = SQLModelCRUDRouter.from_engine(model=Item, engine=engine, paginate=10)
app.include_router(item_router)

# --- Startup Event: Create Tables ---
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# --- Redirect Root to Docs ---
@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/docs")

# ---  THAT'S IT!  Run the app: ---
# uvicorn app:app --reload

# --- Example Usage (using curl) ---
# Create an item:
# curl -X POST -H "Content-Type: application/json" -d '{"name": "My First Item", "description": "This is awesome!"}' http://localhost:8000/item/
# Get all items:
# curl http://localhost:8000/item/
# Get a specific item (replace 1 with the actual ID):
# curl http://localhost:8000/item/1
# Update an item:
# curl -X PUT -H "Content-Type: application/json" -d '{"name": "Updated Item Name"}' http://localhost:8000/item/1
# Delete an item:
# curl -X DELETE http://localhost:8000/item/1
# Delete all items
# curl -X DELETE http://localhost:8000/item/
```

This single file demonstrates the core functionality.  You can run this directly with `uvicorn app:app --reload`.  It creates an in-memory SQLite database, defines the `Item` model, creates the CRUD routes, and sets up the FastAPI application. This is the *best* onboarding experience, as it's fully self-contained and runnable.

## Detailed Usage

### 1. Define Your SQLModel

```python
# models.py
from sqlmodel import SQLModel, Field

class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str | None = None
```

### 2. Create Your FastAPI App and Router

```python
# main.py
from fastapi import FastAPI
from sqlmodel import create_engine
from crudcrud import SQLModelCRUDRouter
from models import Item  # Import your model

# Database URL (replace with your actual database URL)
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=True)

# Create the FastAPI app
app = FastAPI()

# Create the CRUD router using .from_engine() (recommended)
item_router = SQLModelCRUDRouter.from_engine(model=Item, engine=engine, paginate=20)
app.include_router(item_router)

# Optional: Create tables on startup (good for development)
from sqlmodel import SQLModel
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

```

### 3. Run Your Application

```bash
uvicorn main:app --reload
```

Now you have a fully functional API with endpoints for:

*   **GET `/item/`**: Get all items (paginated).
*   **GET `/item/{item_id}`**: Get a specific item by ID.
*   **POST `/item/`**: Create a new item.
*   **PUT `/item/{item_id}`**: Update an existing item.
*   **DELETE `/item/{item_id}`**: Delete an item.
*   **DELETE `/item/`**: Delete all items.

### Advanced Usage: Customizing CRUD Operations

If you need more control over the CRUD operations, you can override the default `SQLModelCRUD` methods or provide your own `get_crud` callable to the `SQLModelCRUDRouter`.

```python
# custom_crud.py
from crudcrud import SQLModelCRUD
from models import Item
from sqlmodel import Session

class CustomItemCRUD(SQLModelCRUD[Item]):
    def get_all(self, skip: int = 0, limit: int = 100, session: Session | None = None):
        # Implement custom logic for getting all items, e.g., filtering
        print("Using custom get_all")
        return super().get_all(skip, limit, session)

# main.py (using the custom CRUD class)
from fastapi import FastAPI
from sqlmodel import create_engine
from crudcrud import SQLModelCRUDRouter
from models import Item
from custom_crud import CustomItemCRUD # Import your Custom CRUD

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=True)
app = FastAPI()

# Pass a custom get_crud callable to from_engine
item_router = SQLModelCRUDRouter.from_engine(
    model=Item, engine=engine, get_crud=lambda m: CustomItemCRUD(m, engine=engine)
)
app.include_router(item_router)

from sqlmodel import SQLModel
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
```

This example shows how to create a custom `CustomItemCRUD` class that overrides the `get_all` method.  You can similarly override other methods (`get`, `create`, `update`, `delete`, `delete_all`) to implement custom logic.  The key is to pass a callable (in this case, a lambda function that instantiates your custom CRUD class) to the `get_crud` parameter of `SQLModelCRUDRouter.from_engine`.

## Testing

```bash
poetry install  # Install development dependencies (including pytest)
poetry run pytest
```

The tests use an in-memory SQLite database, so no external database setup is required.  The `conftest.py` file provides fixtures for the database engine, session, test model, FastAPI application, and test client.  The test files (`test_crud.py`, `test_crud_router.py`) contain the actual test cases.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Contributing

Contributions are welcome!  Please feel free to submit pull requests or open issues.