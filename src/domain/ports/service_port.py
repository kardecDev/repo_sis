# domain/ports.py
from abc import ABC, abstractmethod

class PasswordServicePort(ABC):
    @abstractmethod
    def hash_password(self, password: str) -> str:
        pass

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pass

    @abstractmethod
    def validate_password_strength(self, password: str) -> bool:
        pass

class TokenServicePort(ABC):
    @abstractmethod
    def create_access_token(self, data: dict) -> str:
        pass

    @abstractmethod
    def create_refresh_token(self, data: dict) -> str:
        pass

    @abstractmethod
    def verify_token(self, token: str) -> dict:
        pass

    @abstractmethod
    def get_token_expiration(self) -> int:
        pass

class RateLimiterPort(ABC):
    @abstractmethod
    async def is_rate_limited(self, key: str, limit: int, window: int) -> bool:
        pass

    @abstractmethod
    async def increment_counter(self, key: str, window: int) -> int:
        pass