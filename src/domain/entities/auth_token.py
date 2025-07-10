# domain/auth_token.py
from dataclasses import dataclass

@dataclass
class AuthToken:
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int