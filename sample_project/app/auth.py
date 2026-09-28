"""Authentication and session token service."""
import hashlib
import time
from typing import Any, Dict, Optional
from app.database import db


class AuthService:
    def __init__(self, database=db, token_ttl_seconds: int = 3600) -> None:
        self.db = database
        self.ttl = token_ttl_seconds

    def hash_password(self, password: str, salt: str = "app_salt") -> str:
        salted = f"{salt}:{password}".encode("utf-8")
        return hashlib.sha256(salted).hexdigest()

    def generate_token(self, user_id: str) -> str:
        timestamp = str(time.time()).encode("utf-8")
        token = hashlib.sha1(f"{user_id}:{timestamp}".encode("utf-8")).hexdigest()
        expires_at = time.time() + self.ttl
        self.db.insert("tokens", token, {
            "user_id": user_id,
            "expires_at": expires_at,
        })
        return token

    def validate_token(self, token: str) -> Optional[str]:
        record = self.db.get("tokens", token)
        if not record:
            return None
        if time.time() > record["expires_at"]:
            return None
        return str(record["user_id"])

    def revoke_token(self, token: str) -> bool:
        record = self.db.get("tokens", token)
        if not record:
            return False
        # Set expired
        self.db.update("tokens", token, {"expires_at": 0})
        return True
