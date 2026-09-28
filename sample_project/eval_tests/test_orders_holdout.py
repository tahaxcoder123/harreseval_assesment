"""Holdout tests for order total calculations (Task 2)."""
import pytest
from app.database import db
from app.orders import OrderService


@pytest.fixture(autouse=True)
def clean_db():
    db.clear()
    yield
    db.clear()


def test_order_discount_subtracted():
    service = OrderService(db)
    items = [
        {"price": 100.0, "quantity": 1},
        {"price": 50.0, "quantity": 2},
    ]  # subtotal = 200.0
    
    # 20% discount -> discount = 40.0
    # taxable = 160.0, 10% tax -> 16.0
    # total = 176.0 (not 200 + 40 + 16 = 256)
    res = service.calculate_total(items, discount_rate=0.20, tax_rate=0.10)
    assert res["subtotal"] == 200.0
    assert res["discount"] == 40.0
    assert res["tax"] == 16.0
    assert res["total"] == 176.0, f"Expected 176.0, got {res['total']}"
