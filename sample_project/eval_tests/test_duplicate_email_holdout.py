"""Holdout tests for duplicate email validation (Task 3)."""
import pytest
from app.database import db
from app.users import UserService


@pytest.fixture(autouse=True)
def clean_db():
    db.clear()
    yield
    db.clear()


def test_duplicate_email_rejected():
    service = UserService(db)
    service.create_user("u1", "test@domain.com", "Test User")

    # Duplicate should raise ValueError
    with pytest.raises(ValueError, match="(?i)email.*already"):
        service.create_user("u2", "test@domain.com", "Duplicate User")

    # Case insensitive duplicate should also raise ValueError
    with pytest.raises(ValueError, match="(?i)email.*already"):
        service.create_user("u3", "TEST@DOMAIN.COM", "Caps User")
