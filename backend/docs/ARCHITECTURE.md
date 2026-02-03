# Backend Architecture & API Design

## Architecture Overview

```
FastAPI Application
├── CORS Middleware (frontend integration)
├── Routers (API endpoints)
├── Schemas (request/response validation)
├── Services (business logic)
├── Repository Layer (data access)
├── Database (PostgreSQL)
└── External APIs (future)
```

## Layer Breakdown

### 1. API Router Layer (`app/api/`)
- **Purpose**: Define HTTP endpoints
- **Responsibilities**:
  - Accept requests
  - Validate input schemas
  - Call service layer
  - Return formatted responses
- **Files**:
  - `routes.py` - Endpoint definitions

### 2. Service Layer (`app/services/`)
- **Purpose**: Encapsulate business logic
- **Responsibilities**:
  - User authentication
  - Data validation & transformation
  - Orchestration between repositories
- **Example**:
  ```python
  class AuthService:
      async def login(self, email: str, password: str) -> dict:
          user = await self.user_repo.get_by_email(email)
          if not user or not verify_password(password, user.hashed_password):
              raise AuthenticationError()
          token = create_access_token(user.id)
          return {"access_token": token, "user": user}
  ```

### 3. Repository Layer (`app/repositories/`)
- **Purpose**: Data access abstraction
- **Responsibilities**:
  - Query database
  - Create, read, update, delete operations
  - Handle database errors
- **Example**:
  ```python
  class UserRepository:
      async def get_by_email(self, email: str) -> User | None:
          return await db.query(User).filter_by(email=email).first()
  ```

### 4. Models Layer (`app/models/`)
- **Purpose**: Database schema definitions
- **Tool**: SQLAlchemy ORM
- **Example**:
  ```python
  class User(Base):
      __tablename__ = "users"
      id: Mapped[str] = mapped_column(primary_key=True)
      email: Mapped[str] = mapped_column(unique=True)
      hashed_password: Mapped[str]
      created_at: Mapped[datetime]
  ```

### 5. Schemas Layer (`app/schemas/`)
- **Purpose**: Request/response validation
- **Tool**: Pydantic
- **Example**:
  ```python
  class LoginRequest(BaseModel):
      email: EmailStr
      password: str = Field(..., min_length=8)
  ```

### 6. Core Layer (`app/core/`)
- **Purpose**: Shared utilities & configuration
- **Files**:
  - `config.py` - Settings management
  - `security.py` - JWT, password hashing
  - `exceptions.py` - Custom exceptions

## Request Flow

```
HTTP Request
    ↓
Router Endpoint
    ↓
Pydantic Validation (Schema)
    ↓
Service Business Logic
    ↓
Repository Data Access
    ↓
Database
    ↓
Response Serialization
    ↓
HTTP Response (JSON)
```

## Database Layer Setup

### Session Management
```python
# app/db/session.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

engine = create_async_engine(settings.database_url, echo=False)

async def get_db_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session
```

### Dependency Injection
```python
@router.post("/auth/login")
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db_session),
) -> LoginResponse:
    service = AuthService(db)
    result = await service.login(request.email, request.password)
    return result
```

## Authentication Flow

### 1. User Registration
```
POST /auth/signup
{
  "email": "user@example.com",
  "password": "secure_password",
  "first_name": "John",
  "last_name": "Doe"
}
    ↓
Validate input
    ↓
Hash password with bcrypt
    ↓
Store user in database
    ↓
Return user object with success message
```

### 2. User Login
```
POST /auth/login
{
  "email": "user@example.com",
  "password": "secure_password"
}
    ↓
Find user by email
    ↓
Verify password hash
    ↓
Generate JWT access token
    ↓
Return token & user info
```

### 3. Protected Routes
```
GET /api/v1/protected-endpoint
Authorization: Bearer <access_token>
    ↓
Decode JWT token
    ↓
Extract user ID
    ↓
Validate token expiration
    ↓
Proceed with request
```

## JWT Token Structure

```
Header: { "alg": "HS256", "typ": "JWT" }
Payload: {
  "sub": "user-id",
  "email": "user@example.com",
  "exp": 1234567890,
  "iat": 1234567800
}
Signature: HMACSHA256(header.payload, SECRET_KEY)
```

## Error Handling

### Standard Error Response
```json
{
  "detail": "String error message",
  "status_code": 400
}
```

### Custom Exception Classes
```python
class SmartAuditException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

class AuthenticationError(SmartAuditException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(401, detail)
```

## CORS Configuration

```python
# Middleware in main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # ["http://localhost:3000", ...]
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE, OPTIONS
    allow_headers=["*"],  # Content-Type, Authorization, etc.
)
```

## Configuration Management

### Environment-based Settings
```python
# app/core/config.py
class Settings(BaseSettings):
    app_name: str = "Smart Audit Agent"
    env: str = "development"
    database_url: str = "postgresql://..."
    secret_key: str = "change-me"
    cors_origins: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

## Logging & Monitoring

### Structured Logging
```python
import logging
logger = logging.getLogger(__name__)

logger.info("User login successful", extra={"user_id": user.id, "email": user.email})
logger.error("Database connection failed", exc_info=True)
```

## Testing Strategy

### Unit Tests
```python
# tests/test_auth.py
async def test_login_success():
    service = AuthService(db_mock)
    result = await service.login("user@example.com", "password123")
    assert result["access_token"] is not None
```

### Integration Tests
```python
async def test_login_endpoint(client: TestClient):
    response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

## Deployment

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app"]
```

### Environment Variables for Production
```bash
ENV=production
DATABASE_URL=postgresql://prod_user:prod_pass@prod_db:5432/audit
SECRET_KEY=<generate-strong-key>
CORS_ORIGINS=["https://smartaudit.com", "https://www.smartaudit.com"]
LOG_LEVEL=warning
```

## Performance Considerations

### Database Query Optimization
- Use ORM relationships with lazy loading
- Add database indexes on frequently queried fields
- Use connection pooling (SQLAlchemy default)

### Async/Await
- All I/O operations (DB, HTTP) are async
- Use `async def` for route handlers
- Leverage async context managers

### Caching (Future)
- Implement Redis caching for user sessions
- Cache authentication tokens
- TTL-based cache invalidation

## Security Hardening

### Checklist
- [ ] Strong password hashing (bcrypt)
- [ ] JWT token expiration
- [ ] SQL injection prevention (ORM)
- [ ] CORS properly configured
- [ ] Rate limiting middleware
- [ ] Input validation (Pydantic)
- [ ] Secrets management (environment variables)
- [ ] HTTPS in production

## Next Steps

1. Implement database models and migrations
2. Build repository layer for data access
3. Implement service layer with business logic
4. Add authentication middleware for protected routes
5. Write comprehensive tests
6. Setup logging and monitoring
7. Deploy to production environment
