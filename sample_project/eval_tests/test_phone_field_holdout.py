"""Holdout test for phone_number field validation (Task 6)."""
import pytest
from app.database import db
from app.users import UserService


@pytest.fixture(autouse=True)
def clean_db():
    db.clear()
    yield
    db.clear()


def test_valid_phone_number_saved():
    service = UserService(db)
    u = service.create_user("u1", "alice@example.com", "Alice", phone_number="+1-555-0199")
    assert u.get("phone_number") == "+1-555-0199"


def test_invalid_short_phone_number_rejected():
    service = UserService(db)
    with pytest.raises(ValueError, match="(?i)phone"):
        service.create_user("u2", "bob@example.com", "Bob", phone_number="123")


def test_phone_number_optional_backward_compatibility():
    service = UserService(db)
    u = service.create_user("u3", "charlie@example.com", "Charlie")
    assert "id" in u
