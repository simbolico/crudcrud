import pytest
from crudcrud import SQLModelCRUD
from crudcrud.exceptions import ItemNotFoundException

@pytest.fixture(autouse=True)
def clear_crud(engine, test_model):
    SQLModelCRUD(test_model, engine=engine).delete_all()

def test_create_item(engine, test_model):
    crud = SQLModelCRUD(test_model, engine=engine)
    item = crud.create({"name": "create test"})
    print("Created:", item)
    assert item.id is not None

def test_get_item(engine, test_model):
    crud = SQLModelCRUD(test_model, engine=engine)
    item = crud.create({"name": "get test"})
    fetched = crud.get(item.id)
    print("Fetched:", fetched)
    assert fetched.name == "get test"

def test_get_all(engine, test_model):
    crud = SQLModelCRUD(test_model, engine=engine)
    items = [crud.create({"name": f"item {i}"}) for i in range(3)]
    all_items = crud.get_all()
    print("All items:", all_items)
    assert len(all_items) == 3

def test_update_item(engine, test_model):
    crud = SQLModelCRUD(test_model, engine=engine)
    item = crud.create({"name": "old"})
    updated = crud.update(item.id, {"name": "new"})
    print("Updated:", updated)
    assert updated.name == "new"

def test_delete_item(engine, test_model):
    crud = SQLModelCRUD(test_model, engine=engine)
    item = crud.create({"name": "delete test"})
    deleted = crud.delete(item.id)
    print("Deleted:", deleted)
    with pytest.raises(ItemNotFoundException):
        crud.get(item.id)

def test_delete_all(engine, test_model):
    crud = SQLModelCRUD(test_model, engine=engine)
    for i in range(2):
        crud.create({"name": f"temp {i}"})
    crud.delete_all()
    all_items = crud.get_all()
    print("After delete all:", all_items)
    assert all_items == []
