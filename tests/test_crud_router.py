import pytest

@pytest.fixture(autouse=True)
def clear_db(client):
    client.delete("/testitem")

def test_create_item_endpoint(client):
    r = client.post("/testitem", json={"name": "endpoint create"})
    print("Create endpoint:", r.json())
    assert r.status_code == 200
    data = r.json()
    assert "id" in data and data["name"] == "endpoint create"

def test_get_all_endpoint(client):
    client.post("/testitem", json={"name": "item 1"})
    client.post("/testitem", json={"name": "item 2"})
    r = client.get("/testitem")
    print("Get all endpoint:", r.json())
    assert r.status_code == 200
    assert isinstance(r.json(), list) and len(r.json()) >= 2

def test_get_item_endpoint(client):
    r1 = client.post("/testitem", json={"name": "single item"})
    item_id = r1.json()["id"]
    r2 = client.get(f"/testitem/{item_id}")
    print("Get single endpoint:", r2.json())
    assert r2.status_code == 200 and r2.json()["id"] == item_id

def test_update_item_endpoint(client):
    r1 = client.post("/testitem", json={"name": "before update"})
    item_id = r1.json()["id"]
    r2 = client.put(f"/testitem/{item_id}", json={"name": "after update"})
    print("Update endpoint:", r2.json())
    assert r2.status_code == 200 and r2.json()["name"] == "after update"

def test_delete_item_endpoint(client):
    r1 = client.post("/testitem", json={"name": "to delete"})
    item_id = r1.json()["id"]
    r2 = client.delete(f"/testitem/{item_id}")
    print("Delete item endpoint:", r2.json())
    assert r2.status_code == 200
    r3 = client.get(f"/testitem/{item_id}")
    print("Get deleted item endpoint:", r3.json())
    assert r3.status_code == 404

def test_delete_all_endpoint(client):
    client.post("/testitem", json={"name": "bulk 1"})
    client.post("/testitem", json={"name": "bulk 2"})
    r1 = client.delete("/testitem")
    print("Delete all endpoint:", r1.json())
    assert r1.status_code == 200
    r2 = client.get("/testitem")
    print("After delete all endpoint:", r2.json())
    assert r2.json() == []
