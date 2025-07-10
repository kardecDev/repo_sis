# domain/login_attempt.py
from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class LoginAttempt:
    id: Optional[int]
    username: str
    ip_address: str
    success: bool
    attempted_at: datetime
    user_agent: Optional[str]