# api/controllers.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from redis import aioredis
from domain.services import AuthService
from infrastructure.repositories import PostgresUserRepository, PostgresLoginAttemptRepository
from infrastructure.security.password_service import BcryptPasswordService
from infrastructure.security.token_service import JWTTokenService
from infrastructure.security.rate_limiter import RedisRateLimiter
from api.schemas import (
    UserRegisterRequest, 
    UserLoginRequest, 
    TokenResponse, 
    RefreshTokenRequest,
    UserResponse,
    ErrorResponse
)

# Import or create redis_client (example using aioredis)

redis_client = aioredis.from_url("redis://localhost")  # Update with your Redis config

router = APIRouter()
security = HTTPBearer()

# Dependency injection (simplified - should be configured properly)
async def get_auth_service(session: AsyncSession) -> AuthService:
    user_repo = PostgresUserRepository(session)
    login_attempt_repo = PostgresLoginAttemptRepository(session)
    password_service = BcryptPasswordService()
    token_service = JWTTokenService("your-secret-key-here")  # Should be from config
    rate_limiter = RedisRateLimiter(redis_client)  # Should be injected
    
    return AuthService(
        user_repo,
        login_attempt_repo,
        password_service,
        token_service,
        rate_limiter
    )

@router.post("/register", response_model=UserResponse)
async def register(
    request: UserRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        user = await auth_service.register_user(
            request.username,
            request.email,
            request.password
        )
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            last_login=user.last_login,
            created_at=user.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=TokenResponse)
async def login(
    request: UserLoginRequest,
    http_request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    ip_address = http_request.client.host
    user_agent = http_request.headers.get("user-agent")
    
    token, message = await auth_service.authenticate_user(
        request.username,
        request.password,
        ip_address,
        user_agent
    )
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message
        )
    
    return TokenResponse(
        access_token=token.access_token,
        refresh_token=token.refresh_token,
        token_type=token.token_type,
        expires_in=token.expires_in
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    token = await auth_service.refresh_token(request.refresh_token)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    return TokenResponse(
        access_token=token.access_token,
        refresh_token=token.refresh_token,
        token_type=token.token_type,
        expires_in=token.expires_in
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.get_current_user(credentials.credentials)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        last_login=user.last_login,
        created_at=user.created_at
    )