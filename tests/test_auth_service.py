# tests/test_auth_service.py
import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timedelta
from domain.services import AuthService
from domain.entities import User, LoginAttempt

@pytest.fixture
def auth_service():
    user_repo = AsyncMock()
    login_attempt_repo = AsyncMock()
    password_service = AsyncMock()
    token_service = AsyncMock()
    rate_limiter = AsyncMock()
    
    return AuthService(
        user_repo,
        login_attempt_repo,
        password_service,
        token_service,
        rate_limiter
    )

@pytest.mark.asyncio
async def test_register_user_success(auth_service):
    # Mock dependencies
    auth_service.password_service.validate_password_strength.return_value = True
    auth_service.user_repository.get_user_by_username.return_value = None
    auth_service.user_repository.get_user_by_email.return_value = None
    auth_service.password_service.hash_password.return_value = "hashed_password"
    
    expected_user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        is_active=True,
        failed_attempts=0,
        locked_until=None,
        last_login=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    auth_service.user_repository.create_user.return_value = expected_user
    
    # Test registration
    result = await auth_service.register_user("testuser", "test@example.com", "SecurePass123!")
    
    assert result.username == "testuser"
    assert result.email == "test@example.com"
    assert result.is_active is True

@pytest.mark.asyncio
async def test_authenticate_user_success(auth_service):
    # Mock user
    user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        is_active=True,
        failed_attempts=0,
        locked_until=None,
        last_login=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Mock dependencies
    auth_service.rate_limiter.is_rate_limited.return_value = False
    auth_service.user_repository.get_user_by_username.return_value = user
    auth_service.password_service.verify_password.return_value = True
    auth_service.token_service.create_access_token.return_value = "access_token"
    auth_service.token_service.create_refresh_token.return_value = "refresh_token"
    auth_service.token_service.get_token_expiration.return_value = 900
    
    # Test authentication
    token, message = await auth_service.authenticate_user(
        "testuser", "password", "127.0.0.1", "test-agent"
    )
    
    assert token is not None
    assert token.access_token == "access_token"
    assert token.refresh_token == "refresh_token"
    assert message == "Login successful"

@pytest.mark.asyncio
async def test_authenticate_user_rate_limited(auth_service):
    # Mock rate limiting
    auth_service.rate_limiter.is_rate_limited.return_value = True
    
    # Test authentication
    token, message = await auth_service.authenticate_user(
        "testuser", "password", "127.0.0.1", "test-agent"
    )
    
    assert token is None
    assert "Rate limit exceeded" in message