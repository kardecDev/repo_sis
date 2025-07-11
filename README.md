
# Secure Login System - FastAPI with Hexagonal Architecture

## Features

### Security Features

- ✅ Secure password hashing with bcrypt and salt
- ✅ JWT tokens with access/refresh mechanism
- ✅ Rate limiting to prevent brute force attacks
- ✅ Account lockout after failed attempts
- ✅ IP-based request tracking
- ✅ Password strength validation
- ✅ Secure headers and HTTPS enforcement
- ✅ Comprehensive logging and monitoring

### Architecture

- ✅ Hexagonal Architecture (Ports and Adapters)
- ✅ Clean separation of concerns
- ✅ Dependency injection
- ✅ Repository pattern
- ✅ Domain-driven design principles

## Quick Start

1. **Clone and setup:**

   ```bash
   git clone <repository>
   cd secure-login-system
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Using Docker (Recommended):**

   ```bash
   make docker-up
   ```

3. **Manual setup:**

   ```bash
   make install
   make migrate
   make run
   ```

## API Endpoints

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/logout` - Logout user

## Security Configuration

The system implements multiple layers of security:

1. **Password Security**: Bcrypt with 12 rounds
2. **Rate Limiting**: 5 attempts per 15 minutes per IP
3. **Account Lockout**: 5 failed attempts locks account for 15 minutes
4. **Token Security**: Short-lived access tokens (15 min) with refresh tokens
5. **Request Logging**: All authentication attempts are logged

## Testing

```bash
make test
```

## Production Deployment

1. Set strong `SECRET_KEY` in environment
2. Configure proper database credentials
3. Set up SSL certificates
4. Configure Redis for production
5. Set up proper monitoring and logging
6. Configure firewalls and security groups

This system follows security best practices and provides a robust foundation for authentication in production applications.
