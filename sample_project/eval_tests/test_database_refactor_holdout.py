"""Holdout test for database context manager refactor (Task 5)."""
import pytest
from app.database import db


@pytest.fixture(autouse=True)
def clean_db():
    db.clear()
    yield
    db.clear()


def test_transaction_context_manager_commit():
    assert hasattr(db, "transaction"), "Database should provide a transaction() context manager"
    with db.transaction():
        db.insert("users", "u1", {"name": "Alice"})
    assert db.get("users", "u1") is not None


def test_transaction_context_manager_rollback_on_error():
    assert hasattr(db, "transaction"), "Database should provide a transaction() context manager"
    try:
        with db.transaction():
            db.insert("users", "u2", {"name": "Bob"})
            raise RuntimeError("Simulated failure")
    except RuntimeError:
        pass
    assert db.get("users", "u2") is None, "Failed transaction changes must be rolled back"
