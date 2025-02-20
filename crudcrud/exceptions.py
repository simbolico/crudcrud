# crudcrud/exceptions.py

class CrudException(Exception):
    """Base exception for CRUD operations."""
    pass

class ItemNotFoundException(CrudException):
    """Raised when an item is not found."""
    pass