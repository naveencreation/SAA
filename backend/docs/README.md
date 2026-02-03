# Smart Audit Agent Backend API

Professional FastAPI backend with industry-standard authentication, database integration, and API documentation.

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 14+ (or Docker)
- pip or uv

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

### Environment Variables (.env)

```bash
# Application
APP_NAME="Smart Audit Agent"
ENV=development
LOG_LEVEL=info

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/smart_audit

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (for frontend)
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001"]
```

### Run Development Server

```bash
# Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server runs on `http://localhost:8000`

- **Interactive API docs**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative docs**: `http://localhost:8000/redoc` (ReDoc)

## API Endpoints

### Health & Status
- `GET /` - API root with version info
- `GET /health` - Health check
- `GET /config` - Configuration summary (no secrets)

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/signup` - User registration
- `GET /api/v1/auth/me` - Current user profile

## Project Structure

```
Backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app with middleware
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # API endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Settings management
│   │   └── security.py        # JWT & password utilities (TODO)
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py            # SQLAlchemy base (TODO)
│   │   └── session.py         # Database session (TODO)
│   ├── models/                # SQLAlchemy models (TODO)
│   ├── schemas/               # Pydantic schemas (TODO)
│   ├── services/              # Business logic (TODO)
│   ├── repositories/          # Data access (TODO)
│   └── utils/                 # Helper functions
├── tests/                      # Unit & integration tests
├── .env.example
├── main.py
└── requirements.txt
```

## Tech Stack
- **Framework**: FastAPI 0.115.4
- **Server**: Uvicorn + Gunicorn
- **Database**: PostgreSQL + SQLAlchemy
- **Validation**: Pydantic 2.9.2
- **Auth**: JWT + BCrypt
- **CORS**: python-multipart

## Key Features

### CORS Middleware
- Configured for Next.js frontend development
- Allows credentials and all common HTTP methods
- Extensible via environment variables

### Configuration Management
- Pydantic Settings for environment-based config
- Single source of truth via `get_settings()`
- Type-safe configuration with validation

### API Documentation
- Auto-generated Swagger UI at `/docs`
- Interactive request testing
- Request/response schemas

## Development Workflow

### Code Quality
```bash
# Linting
ruff check .

# Formatting
black . --line-length=100

# Type checking
mypy app
```

### Testing
```bash
pytest tests/
pytest --cov=app tests/  # With coverage
```

### Database Migrations
```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Docker Deployment

```bash
# Build image
docker build -t smart-audit-backend .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@db:5432/audit \
  -e SECRET_KEY=your-secret \
  smart-audit-backend
```

## Production Checklist
- [ ] Set unique `SECRET_KEY` in production
- [ ] Update `ENV=production`
- [ ] Configure PostgreSQL with strong credentials
- [ ] Set appropriate `CORS_ORIGINS`
- [ ] Enable logging and monitoring
- [ ] Use gunicorn with multiple workers
- [ ] Setup reverse proxy (nginx/caddy)
- [ ] Enable HTTPS/SSL

## Security Best Practices
- Password hashing with bcrypt
- JWT for stateless authentication
- CORS properly configured
- SQL injection prevention via ORM
- XSS protection headers (to be added)
- Rate limiting (to be implemented)

## Frontend Integration

The frontend (Next.js) is configured to call this API:

```typescript
const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL;
// http://localhost:8000

const response = await fetch(`${apiBase}/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password }),
});
```

## Documentation References
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [JWT Introduction](https://jwt.io/introduction)

## Contributing
See [CONTRIBUTING.md](./docs/CONTRIBUTING.md) for guidelines.

## License
Proprietary - Smart Audit Agent
