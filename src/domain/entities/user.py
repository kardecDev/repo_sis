# domain/user.py
from datetime import datetime
from typing import Optional
from dataclasses import dataclass

@dataclass
class User:
    id: Optional[int]
    username: str
    email: str
    password_hash: str
    is_active: bool
    failed_attempts: int
    locked_until: Optional[datetime]
    last_login: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]