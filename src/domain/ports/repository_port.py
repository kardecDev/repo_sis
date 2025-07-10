# domain/repository_ports.py
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List
from domain.entities import User, LoginAttempt

class UserRepositoryPort(ABC):
    @abstractmethod
    async def create_user(self, user: User) -> User:
        pass

    @abstractmethod
    async def get_user_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def update_user(self, user: User) -> User:
        pass

    @abstractmethod
    async def increment_failed_attempts(self, username: str) -> None:
        pass

    @abstractmethod
    async def reset_failed_attempts(self, username: str) -> None:
        pass

    @abstractmethod
    async def lock_user(self, username: str, until: datetime) -> None:
        pass

class LoginAttemptRepositoryPort(ABC):
    @abstractmethod
    async def create_login_attempt(self, attempt: LoginAttempt) -> LoginAttempt:
        pass

    @abstractmethod
    async def get_recent_attempts(self, ip_address: str, minutes: int) -> List[LoginAttempt]:
        pass