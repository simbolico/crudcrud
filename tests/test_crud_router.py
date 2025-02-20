
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlmodel import Session, select
from crudcrud.crud_router import SQLModelCRUDRouter

@pytest.fixture(scope="function")
def app(test_model, engine):
    app = FastAPI()
    router = SQLModelCRUDRouter.from_engine(model=test_model, engine=engine)
    app.include_router(router, prefix="/items")  # Add prefix to avoid root path conflicts
    return app

@pytest.fixture(scope="function")
def client(app, session, test_model):
    # Clear database before each test
    session.query(test_model).delete()
    session.commit()
    return TestClient(app)

def test_create_item(client, test_model):
    response = client.post("/items/", json={"name": "Test Item", "value": 25.5})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["value"] == 25.5
    assert "id" in data

def test_get_all_items(client, test_model):
    client.post("/items/", json={"name": "Item 1", "value": 1.0})
    client.post("/items/", json={"name": "Item 2", "value": 2.0})
    response = client.get("/items/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Item 1"
    assert data[1]["name"] == "Item 2"

def test_get_item(client, test_model):
    create_response = client.post("/items/", json={"name": "Get Me", "value": 5.0})
    assert create_response.status_code == 200
    item_id = create_response.json()["id"]

    get_response = client.get(f"/items/{item_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["name"] == "Get Me"
    assert data["id"] == item_id

def test_get_item_not_found(client, test_model):
    response = client.get("/items/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item with id 999 not found"

def test_update_item(client, test_model):
    create_response = client.post("/items/", json={"name": "Old Name", "value": 10.0})
    item_id = create_response.json()["id"]

    update_response = client.put(f"/items/{item_id}", json={"name": "New Name", "value": 15.0})
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "New Name"
    assert data["value"] == 15.0

def test_update_item_not_found(client, test_model):
    response = client.put("/items/999", json={"name": "Doesn't Matter"})
    assert response.status_code == 404

def test_delete_item(client, test_model):
    create_response = client.post("/items/", json={"name": "Delete Me", "value": 5.0})
    item_id = create_response.json()["id"]

    delete_response = client.delete(f"/items/{item_id}")
    assert delete_response.status_code == 200

    get_response = client.get(f"/items/{item_id}")
    assert get_response.status_code == 404

def test_delete_all_items(client, test_model):
    client.post("/items/", json={"name": "Item 1", "value": 1.0})
    client.post("/items/", json={"name": "Item 2", "value": 2.0})

    delete_response = client.delete("/items/")
    assert delete_response.status_code == 200
    assert delete_response.json() == []

    get_response = client.get("/items/")
    assert get_response.status_code == 200
    assert get_response.json() == []
