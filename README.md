# crudcrud

A simple CRUD library built with FastAPI and SQLModel.

## Installation

```bash
pip install crudcrud
```

## Usage
```python
#app.py as an example
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from sqlmodel import SQLModel, create_engine, Field
from crudcrud import SQLModelCRUDRouter

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=False)

# Define database models
class ItemCreate(SQLModel):
name: str
description: str | None = None

class Item(ItemCreate, table=True):
id: int | None = Field(default=None, primary_key=True)

SQLModel.metadata.create_all(engine)

app = FastAPI()

# Use the class method to create routers without the user having to define the session dependency.
item_router = SQLModelCRUDRouter.from_engine(model=Item, engine=engine, paginate=10)
app.include_router(item_router)

@app.get("/", include_in_schema=False)
async def custom_swagger_ui_html():
return RedirectResponse(url="/docs")

```
## Features
*   Provides a `SQLCRUD` class for basic CRUD operations.
*   Provides a `SQLModelCRUDRouter` class that extends `fastapi.APIRouter` for easy route generation.
*   Uses SQLModel for database models and Pydantic for data validation.
*   Includes custom exceptions for better error handling.
## Testing
```bash
poetry run pytest
```

* **LICENSE**:
Choose a license file (e.g., MIT, Apache 2.0) and put it into the root of the project.

**3. Key Improvements:**

*   **Package Structure:** Organized into a proper Python package (`crudcrud`) with `__init__.py`.
*   **`pyproject.toml`:** Uses Poetry for dependency management and build configuration.  This is *highly* recommended for modern Python projects.  It's much better than `setup.py`.
*   **Versioning:**  Includes a `__version__` in `__init__.py`.
*   **Custom Exceptions:** Creates `CrudException` and `ItemNotFoundException` for more specific error handling within the library.  This makes it easier for users of the library to catch and handle specific errors.
*   **Tests:** Includes comprehensive unit tests using `pytest` and `fastapi.testclient`.  The tests cover all the CRUD operations and the router functionality.  Importantly, the tests use an in-memory SQLite database, so they don't require a separate database setup.
*   **Test Fixtures:** Uses `pytest` fixtures for database setup and teardown, making the tests more organized and efficient.
*   **Error Handling in Router:** The `SQLModelCRUDRouter` now catches `ItemNotFoundException` and other exceptions from the `SQLCRUD` methods and re-raises them as `HTTPException` with appropriate status codes (404 for not found, 422 for validation errors). This is essential for proper API behavior.  The `from e` part preserves the original exception's traceback, which is helpful for debugging.
*   **`from_engine` Improvement:** The `from_engine` method in `SQLModelCRUDRouter` is further improved to ensure `get_crud` is *always* provided.  This prevents potential errors if someone tries to use the router without `from_engine` and forgets to provide a `get_crud` function.
*   **README:** Provides a basic README with installation and usage instructions.
* **Type Hints**: Full type hints are included.
*   **Docstrings**:  You should add comprehensive docstrings to all classes and methods.
* **Return an empty list:** when deleting all items.

**4. How to Use as a Library:**

1.  **Build (using Poetry):**
```bash
poetry build
```
This will create a `.whl` file in the `dist/` directory.

2.  **Install (locally):**
```bash
pip install dist/crudcrud-0.1.0-py3-none-any.whl  # Replace with the actual filename
```

3.  **Install from GitHub (after pushing to a repository):**

```bash
pip install git+https://github.com/<your_username>/<your_repo_name>.git
```

4.  **Use in another project:**
```python
# your_project/main.py
from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine, Field
from crudcrud import SQLModelCRUDRouter

# ... (rest of your code) ...
```

**5. Running tests:**

If you have Poetry installed, you can run the tests using:

```bash
poetry install  # Install dev dependencies
poetry run pytest
```
