"""Database helper and in-memory storage manager."""
from typing import Any, Dict, List, Optional
import copy


class Database:
    """Simple in-memory database helper simulating a relational repository."""

    def __init__(self) -> None:
        self._tables: Dict[str, Dict[str, Dict[str, Any]]] = {
            "users": {},
            "orders": {},
            "tokens": {},
        }
        self._in_transaction: bool = False
        self._snapshot: Optional[Dict[str, Dict[str, Dict[str, Any]]]] = None

    def begin(self) -> None:
        if self._in_transaction:
            raise RuntimeError("Transaction already in progress")
        self._snapshot = copy.deepcopy(self._tables)
        self._in_transaction = True

    def commit(self) -> None:
        if not self._in_transaction:
            raise RuntimeError("No active transaction to commit")
        self._snapshot = None
        self._in_transaction = False

    def rollback(self) -> None:
        if not self._in_transaction:
            raise RuntimeError("No active transaction to rollback")
        if self._snapshot is not None:
            self._tables = self._snapshot
        self._snapshot = None
        self._in_transaction = False

    def insert(self, table: str, item_id: str, record: Dict[str, Any]) -> Dict[str, Any]:
        if table not in self._tables:
            self._tables[table] = {}
        if item_id in self._tables[table]:
            raise ValueError(f"Record with id '{item_id}' already exists in table '{table}'")
        stored = dict(record)
        stored["id"] = item_id
        self._tables[table][item_id] = stored
        return stored

    def get(self, table: str, item_id: str) -> Optional[Dict[str, Any]]:
        return self._tables.get(table, {}).get(item_id)

    def find_all(self, table: str) -> List[Dict[str, Any]]:
        return list(self._tables.get(table, {}).values())

    def update(self, table: str, item_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        record = self.get(table, item_id)
        if record is None:
            return None
        record.update(updates)
        return record

    def clear(self) -> None:
        for t in self._tables:
            self._tables[t].clear()
        self._in_transaction = False
        self._snapshot = None


# Singleton default instance
db = Database()
