"""Unit tests for order service."""
import pytest
from app.database import db
from app.orders import OrderService


@pytest.fixture(autouse=True)
def clean_db():
    db.clear()
    yield
    db.clear()


def test_calculate_total_without_discount():
    service = OrderService(db)
    items = [{"price": 50.0, "quantity": 2}]
    res = service.calculate_total(items, discount_rate=0.0, tax_rate=0.05)
    assert res["subtotal"] == 100.0
    assert res["discount"] == 0.0
    assert res["tax"] == 5.0
    assert res["total"] == 105.0


def test_order_creation_persists():
    service = OrderService(db)
    items = [{"price": 20.0, "quantity": 1}]
    order = service.create_order("o1", "u1", items)
    assert order["id"] == "o1"
    assert order["user_id"] == "u1"
    assert order["subtotal"] == 20.0
