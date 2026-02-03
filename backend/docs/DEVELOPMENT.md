# Backend Development Guide

## Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL 17+ (or Docker Compose)
- Git

### Setup
```bash
cd Backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

## Project Structure

```
Backend/
├── app/
│   ├── main.py              # FastAPI app initialization
│   ├── api/
│   │   └── routes.py        # API endpoints
│   ├── core/
│   │   ├── config.py        # Settings & environment
│   │   └── security.py      # JWT, password utilities (TODO)
│   ├── db/                  # Database layer (TODO)
│   ├── models/              # SQLAlchemy models (TODO)
│   ├── schemas/             # Pydantic request/response (TODO)
│   ├── services/            # Business logic (TODO)
│   ├── repositories/        # Data access layer (TODO)
│   └── utils/               # Helper functions
├── tests/                   # Unit & integration tests (TODO)
├── docs/
│   ├── README.md           # Quick start
│   ├── ARCHITECTURE.md     # System design
│   └── prerequisites.md    # Setup guide
├── requirements.txt        # Python dependencies
├── main.py                 # Application entry point
└── .env.example           # Environment template
```

## API Endpoint Patterns

### Request/Response
```python
from fastapi import APIRouter
from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., min_length=8)

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    # Implementation
    pass
```

### Error Handling
```python
from fastapi import HTTPException, status

@router.post("/auth/login")
async def login(request: LoginRequest):
    if not valid_credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    return response
```

## Database Setup (PostgreSQL)

### Local Development
```bash
# Using Docker Compose
docker-compose up -d db

# Or PostgreSQL directly
createdb smart_audit
psql -d smart_audit -f docker/postgres/init/db-init-pgvector.sql
```

### Connection String
```
postgresql://username:password@localhost:5432/smart_audit
```

## Authentication Implementation

### Step 1: User Model
```python
# app/models/user.py
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
```

### Step 2: Password Utilities
```python
# app/core/security.py
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(user_id: str, expires_delta: timedelta | None = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=30)
    
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": user_id, "exp": expire}
    
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
```

### Step 3: User Repository
```python
# app/repositories/user.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def create(self, email: str, hashed_password: str, first_name: str, last_name: str) -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name
        )
        self.db.add(user)
        await self.db.commit()
        return user
```

### Step 4: Auth Service
```python
# app/services/auth.py
from app.repositories.user import UserRepository
from app.core.security import hash_password, verify_password, create_access_token

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def login(self, email: str, password: str) -> dict:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise Exception("Invalid credentials")  # Use custom exception
        
        token = create_access_token(str(user.id))
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": str(user.id), "email": user.email}
        }
    
    async def signup(self, email: str, password: str, first_name: str, last_name: str) -> dict:
        # Check if user exists
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise Exception("Email already registered")
        
        # Create new user
        hashed = hash_password(password)
        user = await self.user_repo.create(email, hashed, first_name, last_name)
        
        return {
            "message": "User created successfully",
            "user": {"id": str(user.id), "email": user.email}
        }
```

## Testing

### Setup
```bash
pip install pytest pytest-asyncio httpx
```

### Example Test
```python
# tests/test_auth.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_login():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/auth/login",
            json={"email": "user@example.com", "password": "password123"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
```

### Run Tests
```bash
pytest tests/
pytest tests/ --cov=app  # With coverage
```

## Code Quality

### Formatting
```bash
black . --line-length=100
```

### Linting
```bash
ruff check . --fix
```

### Type Checking
```bash
mypy app
```

## Common Development Tasks

### Add New Endpoint
1. Create Pydantic schema in `app/schemas/`
2. Add endpoint handler in `app/api/routes.py`
3. Implement business logic in `app/services/`
4. Write tests in `tests/`

### Add New Database Model
1. Create model class in `app/models/`
2. Create migration with Alembic
3. Create repository in `app/repositories/`
4. Use repository in service layer

## Frontend-Backend Integration

### CORS Configuration
```python
# Already configured in app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # Includes http://localhost:3000
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Base URL
Frontend uses: `http://localhost:8000`

### Example Frontend Call
```typescript
const response = await fetch("http://localhost:8000/auth/login", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ email, password }),
});
```

## Debugging

### Enable Request Logging
```python
# In app/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check API Docs
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Database Debugging
```bash
# Connect to PostgreSQL
psql -d smart_audit

# List tables
\dt

# View user table
SELECT * FROM users;
```

## Docker Deployment

### Build
```bash
docker build -t smart-audit-backend .
```

### Run
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@db:5432/audit \
  -e SECRET_KEY=secret \
  smart-audit-backend
```

### Docker Compose
```bash
docker-compose up backend
```

## Performance Tips

1. **Index frequently queried fields**: `email`, `id`
2. **Use connection pooling**: SQLAlchemy handles this
3. **Implement caching**: Redis for sessions/tokens
4. **Async all I/O**: Always use `async`/`await`
5. **Lazy load relationships**: Avoid N+1 queries

## Production Deployment

### Checklist
- [ ] Generate strong SECRET_KEY: `openssl rand -hex 32`
- [ ] Set ENV=production
- [ ] Use production database URL
- [ ] Setup HTTPS/SSL
- [ ] Configure logging to file/service
- [ ] Use Gunicorn with 4-8 workers
- [ ] Setup reverse proxy (nginx)
- [ ] Monitor application health
- [ ] Setup error tracking (Sentry)

### Gunicorn Command
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```
