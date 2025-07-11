# container.py
from functools import lru_cache
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config.settings import settings
from domain.services import AuthService
from infrastructure.repositories import PostgresUserRepository, PostgresLoginAttemptRepository
from infrastructure.security.password_service import BcryptPasswordService
from infrastructure.security.token_service import JWTTokenService
from infrastructure.security.rate_limiter import RedisRateLimiter

# Database setup
engine = create_async_engine(settings.database_url, echo=False)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@lru_cache()
def get_redis_client():
    return redis.from_url(settings.redis_url)

async def get_db_session():
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_auth_service(session: AsyncSession = None):
    if session is None:
        async with async_session_maker() as session:
            return await _create_auth_service(session)
    return await _create_auth_service(session)

async def _create_auth_service(session: AsyncSession) -> AuthService:
    user_repo = PostgresUserRepository(session)
    login_attempt_repo = PostgresLoginAttemptRepository(session)
    password_service = BcryptPasswordService(rounds=settings.bcrypt_rounds)
    token_service = JWTTokenService(settings.secret_key, settings.algorithm)
    rate_limiter = RedisRateLimiter(get_redis_client())
    
    return AuthService(
        user_repo,
        login_attempt_repo,
        password_service,
        token_service,
        rate_limiter
    )
