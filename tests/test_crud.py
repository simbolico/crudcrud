# tests/test_crud.py
import pytest
from sqlmodel import Session
from crudcrud.crud import SQLCRUD
from crudcrud.exceptions import ItemNotFoundException

def test_create(session: Session, test_model):
    crud = SQLCRUD(test_model, engine=session.get_bind())
    item_data = {"name": "Test Item", "value": 10.5}
    created_item = crud.create(item_data)
    assert created_item.name == "Test Item"
    assert created_item.value == 10.5
    assert created_item.id is not None


def test_get_all(session: Session, test_model):
    crud = SQLCRUD(test_model, engine=session.get_bind())
    item1_data = {"name": "Item 1", "value": 1.0}
    item2_data = {"name": "Item 2", "value": 2.0}
    crud.create(item1_data)
    crud.create(item2_data)
    all_items = crud.get_all()
    assert len(all_items) == 2
    assert all_items[0].name == "Item 1"
    assert all_items[1].name == "Item 2"

def test_get(session: Session, test_model):
    crud = SQLCRUD(test_model, engine=session.get_bind())
    item_data = {"name": "Test Item", "value": 10.5}
    created_item = crud.create(item_data)
    retrieved_item = crud.get(created_item.id)
    assert retrieved_item.name == "Test Item"
    assert retrieved_item.value == 10.5
    assert retrieved_item.id == created_item.id

def test_get_not_found(session: Session, test_model):
    crud = SQLCRUD(test_model, engine=session.get_bind())
    with pytest.raises(ItemNotFoundException):
        crud.get(999)

def test_update(session: Session, test_model):
    crud = SQLCRUD(test_model, engine=session.get_bind())
    item_data = {"name": "Original Name", "value": 5.0}
    created_item = crud.create(item_data)
    updated_data = {"name": "Updated Name", "value": 7.5}
    updated_item = crud.update(created_item.id, updated_data)
    assert updated_item.name == "Updated Name"
    assert updated_item.value == 7.5
    assert updated_item.id == created_item.id

def test_update_not_found(session: Session, test_model):
    crud = SQLCRUD(test_model, engine=session.get_bind())
    with pytest.raises(ItemNotFoundException):
        crud.update(999, {"name": "Doesn't Matter"})

def test_delete(session: Session, test_model):
    crud = SQLCRUD(test_model, engine=session.get_bind())
    item_data = {"name": "To Be Deleted", "value": 20.0}
    created_item = crud.create(item_data)
    deleted_item = crud.delete(created_item.id)
    assert deleted_item.id == created_item.id
    with pytest.raises(ItemNotFoundException):
        crud.get(created_item.id)


def test_delete_not_found(session: Session, test_model):
    crud = SQLCRUD(test_model, engine=session.get_bind())
    with pytest.raises(ItemNotFoundException):
        crud.delete(999)


def test_delete_all(session: Session, test_model):
    crud = SQLCRUD(test_model, engine=session.get_bind())
    crud.create({"name": "Item 1", "value": 1.0})
    crud.create({"name": "Item 2", "value": 2.0})
    crud.delete_all()
    assert len(crud.get_all()) == 0