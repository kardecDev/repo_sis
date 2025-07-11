# infrastructure/database/postgres_login_attempt_epository.py
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.entities import LoginAttempt
from domain.ports import LoginAttemptRepositoryPort
from infrastructure.database.model import LoginAttemptModel


class PostgresLoginAttemptRepository(LoginAttemptRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_login_attempt(self, attempt: LoginAttempt) -> LoginAttempt:
        db_attempt = LoginAttemptModel(
            username=attempt.username,
            ip_address=attempt.ip_address,
            success=attempt.success,
            attempted_at=attempt.attempted_at,
            user_agent=attempt.user_agent
        )
        self.session.add(db_attempt)
        await self.session.commit()
        await self.session.refresh(db_attempt)
        return self._to_entity(db_attempt)

    async def get_recent_attempts(self, ip_address: str, minutes: int) -> List[LoginAttempt]:
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        result = await self.session.execute(
            select(LoginAttemptModel)
            .where(
                LoginAttemptModel.ip_address == ip_address,
                LoginAttemptModel.attempted_at >= cutoff_time
            )
            .order_by(LoginAttemptModel.attempted_at.desc())
        )
        db_attempts = result.scalars().all()
        return [self._to_entity(attempt) for attempt in db_attempts]

    def _to_entity(self, db_attempt: LoginAttemptModel) -> LoginAttempt:
        return LoginAttempt(
            id=db_attempt.id,
            username=db_attempt.username,
            ip_address=db_attempt.ip_address,
            success=db_attempt.success,
            attempted_at=db_attempt.attempted_at,
            user_agent=db_attempt.user_agent
        )