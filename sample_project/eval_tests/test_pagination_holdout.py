"""Holdout tests for pagination (Task 1)."""
import pytest
from app.database import db
from app.users import UserService


@pytest.fixture(autouse=True)
def clean_db():
    db.clear()
    yield
    db.clear()


def test_pagination_holdout():
    service = UserService(db)
    for i in range(12):
        service.create_user(f"u{i}", f"user{i}@example.com", f"User {i}")

    # Backward compatibility: list without page_size
    all_users = service.list_users()
    assert isinstance(all_users, list)
    assert len(all_users) == 12

    # Paginated page 1
    page1 = service.list_users(page=1, page_size=5)
    assert isinstance(page1, dict), "Should return dict when page_size is specified"
    assert len(page1["items"]) == 5
    assert page1["total"] == 12
    assert page1["page"] == 1
    assert page1["total_pages"] == 3

    # Paginated page 3 (remaining 2 items)
    page3 = service.list_users(page=3, page_size=5)
    assert len(page3["items"]) == 2
