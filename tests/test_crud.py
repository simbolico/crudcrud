import pytest
from sqlmodel import Session
from crudcrud.crud import SQLCRUD

def test_crud_init(session, test_model):
    crud = SQLCRUD(test_model, engine=session.get_bind())
    assert crud.model == test_model

def test_get_all(session: Session, test_model):
    crud = SQLCRUD(test_model, engine=session.get_bind())
    session.query(test_model).delete()
    session.commit()

    item1_data = {"name": "Item 1", "value": 1.0}
    item2_data = {"name": "Item 2", "value": 2.0}
    crud.create(item1_data)
    crud.create(item2_data)
    all_items = crud.get_all()
    assert len(all_items) == 2

def test_get(session, test_model):
    crud = SQLCRUD(test_model, engine=session.get_bind())
    item_data = {"name": "Test Item", "value": 10.5}
    created_item = crud.create(item_data)
    fetched_item = crud.get(created_item.id)
    assert fetched_item.id == created_item.id
    assert fetched_item.name == item_data["name"]
    assert fetched_item.value == item_data["value"]

def test_create(session, test_model):
    crud = SQLCRUD(test_model, engine=session.get_bind())
    item_data = {"name": "Test Item", "value": 10.5}
    created_item = crud.create(item_data)
    assert created_item.name == item_data["name"]
    assert created_item.value == item_data["value"]
    assert created_item.id is not None

def test_update(session, test_model):
    crud = SQLCRUD(test_model, engine=session.get_bind())
    item_data = {"name": "Old Name", "value": 10.5}
    created_item = crud.create(item_data)
    updated_data = {"name": "New Name", "value": 15.0}
    updated_item = crud.update(created_item.id, updated_data)
    assert updated_item.id == created_item.id
    assert updated_item.name == updated_data["name"]
    assert updated_item.value == updated_data["value"]

def test_delete(session, test_model):
    crud = SQLCRUD(test_model, engine=session.get_bind())
    item_data = {"name": "Delete Me", "value": 5.0}
    created_item = crud.create(item_data)
    deleted_item = crud.delete(created_item.id)
    assert deleted_item.id == created_item.id
    with pytest.raises(Exception):
        crud.get(created_item.id)

def test_delete_all(session, test_model):
    crud = SQLCRUD(test_model, engine=session.get_bind())
    item1_data = {"name": "Item 1", "value": 1.0}
    item2_data = {"name": "Item 2", "value": 2.0}
    crud.create(item1_data)
    crud.create(item2_data)
    deleted_items = crud.delete_all()
    assert len(crud.get_all()) == 0