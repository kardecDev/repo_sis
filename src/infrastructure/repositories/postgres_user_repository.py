# infrastructure/database/postgres_user_repository.py
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update


from domain.entities import User
from domain.ports import UserRepositoryPort
from infrastructure.database.model import UserModel

class PostgresUserRepository(UserRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user: User) -> User:
        db_user = UserModel(
            username=user.username,
            email=user.email,
            password_hash=user.password_hash,
            is_active=user.is_active,
            failed_attempts=user.failed_attempts,
            locked_until=user.locked_until,
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return self._to_entity(db_user)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        db_user = result.scalar_one_or_none()
        return self._to_entity(db_user) if db_user else None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        db_user = result.scalar_one_or_none()
        return self._to_entity(db_user) if db_user else None

    async def update_user(self, user: User) -> User:
        await self.session.execute(
            update(UserModel)
            .where(UserModel.id == user.id)
            .values(
                username=user.username,
                email=user.email,
                password_hash=user.password_hash,
                is_active=user.is_active,
                failed_attempts=user.failed_attempts,
                locked_until=user.locked_until,
                last_login=user.last_login,
                updated_at=user.updated_at
            )
        )
        await self.session.commit()
        return user

    async def increment_failed_attempts(self, username: str) -> None:
        await self.session.execute(
            update(UserModel)
            .where(UserModel.username == username)
            .values(failed_attempts=UserModel.failed_attempts + 1)
        )
        await self.session.commit()

    async def reset_failed_attempts(self, username: str) -> None:
        await self.session.execute(
            update(UserModel)
            .where(UserModel.username == username)
            .values(failed_attempts=0, locked_until=None)
        )
        await self.session.commit()

    async def lock_user(self, username: str, until: datetime) -> None:
        await self.session.execute(
            update(UserModel)
            .where(UserModel.username == username)
            .values(locked_until=until)
        )
        await self.session.commit()

    def _to_entity(self, db_user: UserModel) -> User:
        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            password_hash=db_user.password_hash,
            is_active=db_user.is_active,
            failed_attempts=db_user.failed_attempts,
            locked_until=db_user.locked_until,
            last_login=db_user.last_login,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
