# config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost/secure_login"

    # Security
    secret_key: str = "your-super-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Password hashing
    bcrypt_rounds: int = 12

    # Rate limiting
    redis_url: str = "redis://localhost:6379"
    max_login_attempts: int = 5
    login_attempt_window_minutes: int = 15

    # Account lockout
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 15

    # CORS
    allowed_origins: list = ["https://yourdomain.com"]

    class Config:
        env_file = ".env"

settings = Settings()