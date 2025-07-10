# domain/services.py
from datetime import datetime, timedelta
from typing import Optional, Tuple
from domain.entities import User, LoginAttempt, AuthToken
from domain.ports import (
    UserRepositoryPort, 
    LoginAttemptRepositoryPort,
    PasswordServicePort,
    TokenServicePort,
    RateLimiterPort
)

class AuthService:
    def __init__(
        self,
        user_repository: UserRepositoryPort,
        login_attempt_repository: LoginAttemptRepositoryPort,
        password_service: PasswordServicePort,
        token_service: TokenServicePort,
        rate_limiter: RateLimiterPort
    ):
        self.user_repository = user_repository
        self.login_attempt_repository = login_attempt_repository
        self.password_service = password_service
        self.token_service = token_service
        self.rate_limiter = rate_limiter
        
        # Security configuration
        self.max_failed_attempts = 5
        self.lockout_duration_minutes = 15
        self.rate_limit_attempts = 5
        self.rate_limit_window_minutes = 15

    async def register_user(self, username: str, email: str, password: str) -> User:
        # Validate password strength
        if not self.password_service.validate_password_strength(password):
            raise ValueError("Password does not meet strength requirements")
        
        # Check if user already exists
        existing_user = await self.user_repository.get_user_by_username(username)
        if existing_user:
            raise ValueError("Username already exists")
        
        existing_email = await self.user_repository.get_user_by_email(email)
        if existing_email:
            raise ValueError("Email already registered")
        
        # Create new user
        password_hash = self.password_service.hash_password(password)
        user = User(
            id=None,
            username=username,
            email=email,
            password_hash=password_hash,
            is_active=True,
            failed_attempts=0,
            locked_until=None,
            last_login=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return await self.user_repository.create_user(user)

    async def authenticate_user(
        self, 
        username: str, 
        password: str, 
        ip_address: str,
        user_agent: Optional[str] = None
    ) -> Tuple[Optional[AuthToken], str]:
        
        # Check rate limiting
        rate_limit_key = f"login_attempts:{ip_address}"
        if await self.rate_limiter.is_rate_limited(
            rate_limit_key, 
            self.rate_limit_attempts, 
            self.rate_limit_window_minutes * 60
        ):
            await self._log_login_attempt(username, ip_address, False, user_agent)
            return None, "Rate limit exceeded. Try again later."
        
        # Get user
        user = await self.user_repository.get_user_by_username(username)
        if not user:
            await self._log_login_attempt(username, ip_address, False, user_agent)
            await self.rate_limiter.increment_counter(rate_limit_key, self.rate_limit_window_minutes * 60)
            return None, "Invalid credentials"
        
        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            await self._log_login_attempt(username, ip_address, False, user_agent)
            return None, f"Account locked until {user.locked_until}"
        
        # Verify password
        if not self.password_service.verify_password(password, user.password_hash):
            await self._handle_failed_login(user, ip_address, user_agent)
            await self.rate_limiter.increment_counter(rate_limit_key, self.rate_limit_window_minutes * 60)
            return None, "Invalid credentials"
        
        # Check if account is active
        if not user.is_active:
            await self._log_login_attempt(username, ip_address, False, user_agent)
            return None, "Account is deactivated"
        
        # Successful login
        await self._handle_successful_login(user, ip_address, user_agent)
        
        # Generate tokens
        token_data = {"sub": user.username, "user_id": user.id}
        access_token = self.token_service.create_access_token(token_data)
        refresh_token = self.token_service.create_refresh_token(token_data)
        
        auth_token = AuthToken(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=self.token_service.get_token_expiration()
        )
        
        return auth_token, "Login successful"

    async def refresh_token(self, refresh_token: str) -> Optional[AuthToken]:
        try:
            payload = self.token_service.verify_token(refresh_token)
            username = payload.get("sub")
            
            if not username:
                return None
            
            user = await self.user_repository.get_user_by_username(username)
            if not user or not user.is_active:
                return None
            
            # Generate new tokens
            token_data = {"sub": user.username, "user_id": user.id}
            access_token = self.token_service.create_access_token(token_data)
            new_refresh_token = self.token_service.create_refresh_token(token_data)
            
            return AuthToken(
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=self.token_service.get_token_expiration()
            )
            
        except Exception:
            return None

    async def get_current_user(self, token: str) -> Optional[User]:
        try:
            payload = self.token_service.verify_token(token)
            username = payload.get("sub")
            
            if not username:
                return None
            
            user = await self.user_repository.get_user_by_username(username)
            return user if user and user.is_active else None
            
        except Exception:
            return None

    async def _handle_failed_login(self, user: User, ip_address: str, user_agent: Optional[str]):
        await self.user_repository.increment_failed_attempts(user.username)
        await self._log_login_attempt(user.username, ip_address, False, user_agent)
        
        # Lock account if too many failed attempts
        if user.failed_attempts + 1 >= self.max_failed_attempts:
            lock_until = datetime.utcnow() + timedelta(minutes=self.lockout_duration_minutes)
            await self.user_repository.lock_user(user.username, lock_until)

    async def _handle_successful_login(self, user: User, ip_address: str, user_agent: Optional[str]):
        await self.user_repository.reset_failed_attempts(user.username)
        await self._log_login_attempt(user.username, ip_address, True, user_agent)
        
        # Update last login
        user.last_login = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        await self.user_repository.update_user(user)

    async def _log_login_attempt(self, username: str, ip_address: str, success: bool, user_agent: Optional[str]):
        attempt = LoginAttempt(
            id=None,
            username=username,
            ip_address=ip_address,
            success=success,
            attempted_at=datetime.utcnow(),
            user_agent=user_agent
        )
        await self.login_attempt_repository.create_login_attempt(attempt)
