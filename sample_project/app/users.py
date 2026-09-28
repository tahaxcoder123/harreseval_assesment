"""User management service and API representation."""
from typing import Any, Dict, List, Optional
from app.database import db


class UserService:
    def __init__(self, database=db) -> None:
        self.db = database

    def create_user(self, user_id: str, email: str, name: str, **extra: Any) -> Dict[str, Any]:
        """Creates a user record. Currently missing duplicate email check!"""
        # Bug/feature gap: Does not check if email already exists in users
        payload = {
            "email": email.strip().lower(),
            "name": name.strip(),
            **extra
        }
        return self.db.insert("users", user_id, payload)

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.db.get("users", user_id)

    def list_users(self) -> List[Dict[str, Any]]:
        """Lists users without pagination."""
        return self.db.find_all("users")
