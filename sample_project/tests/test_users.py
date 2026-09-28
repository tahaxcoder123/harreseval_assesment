"""Unit tests for user service."""
import pytest
from app.database import db
from app.users import UserService


@pytest.fixture(autouse=True)
def clean_db():
    db.clear()
    yield
    db.clear()


def test_create_and_get_user():
    service = UserService(db)
    user = service.create_user("u1", "alice@example.com", "Alice")
    assert user["id"] == "u1"
    assert user["email"] == "alice@example.com"
    assert user["name"] == "Alice"

    fetched = service.get_user("u1")
    assert fetched is not None
    assert fetched["email"] == "alice@example.com"


def test_list_users_basic():
    service = UserService(db)
    service.create_user("u1", "alice@example.com", "Alice")
    service.create_user("u2", "bob@example.com", "Bob")
    users = service.list_users()
    assert len(users) == 2
