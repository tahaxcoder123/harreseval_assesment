"""Order management and price calculation service."""
from typing import Any, Dict, List, Optional
from app.database import db


class OrderService:
    def __init__(self, database=db) -> None:
        self.db = database

    def calculate_total(
        self,
        items: List[Dict[str, Any]],
        discount_rate: float = 0.0,
        tax_rate: float = 0.05,
    ) -> Dict[str, float]:
        """Calculates subtotal, discount, tax, and final total.
        
        KNOWN BUG: The discount is mistakenly ADDED to subtotal instead of subtracted!
        """
        subtotal = 0.0
        for item in items:
            subtotal += float(item.get("price", 0.0)) * int(item.get("quantity", 1))

        # BUG: discount added instead of subtracted
        discount_amount = subtotal * discount_rate
        taxable_amount = max(0.0, subtotal - discount_amount)
        tax_amount = round(taxable_amount * tax_rate, 2)
        
        # Intentional bug in baseline:
        total = round(subtotal + discount_amount + tax_amount, 2)

        return {
            "subtotal": round(subtotal, 2),
            "discount": round(discount_amount, 2),
            "tax": tax_amount,
            "total": total,
        }

    def create_order(
        self,
        order_id: str,
        user_id: str,
        items: List[Dict[str, Any]],
        discount_rate: float = 0.0,
        tax_rate: float = 0.05,
    ) -> Dict[str, Any]:
        totals = self.calculate_total(items, discount_rate, tax_rate)
        record = {
            "user_id": user_id,
            "items": items,
            **totals,
        }
        return self.db.insert("orders", order_id, record)

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        return self.db.get("orders", order_id)
