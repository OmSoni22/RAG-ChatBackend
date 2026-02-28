# FastAPI Enterprise Structure

Production-grade FastAPI application with **SOLID principles**, **MVC architecture**, and **enterprise features**.

## 🚀 Features

- ✅ **SOLID & MVC** - Clean architecture with separation of concerns
- ✅ **Async PostgreSQL** - SQLAlchemy 2.0 with async support
- ✅ **Redis Caching** - Optional Redis integration with decorators
- ✅ **Advanced Logging** - JSON logs with rotation, request ID tracking, queryable API
- ✅ **Error Handling** - Global exception handlers with structured responses
- ✅ **Dependency Injection** - Centralized dependencies for testability
- ✅ **Health Checks** - Liveness/readiness probes for K8s/Docker
- ✅ **CORS** - Configured CORS middleware
- ✅ **OpenAPI** - Auto-generated interactive docs
- ✅ **Testing** - Pytest with async support and fixtures
- ✅ **Alembic Ready** - Prepared for database migrations

## 📁 Project Structure

```
app/
├── api/                 # API routes
│   ├── health.py       # Health check endpoints
│   └── router.py       # Main API router
├── core/               # Core infrastructure
│   ├── cache/         # Redis caching
│   ├── config/        # Configuration & validation
│   ├── db/            # Database setup
│   ├── decorators/    # Reusable decorators
│   ├── exceptions/    # Custom exceptions & handlers
│   └── logging/       # Logging system
├── modules/           # Business modules
│   └── user/          # Example user module
│       ├── services/  # Business logic
│       ├── *_model.py   # SQLAlchemy models
│       ├── *_schema.py  # Pydantic schemas
│       ├── *_repository.py # Data access
│       └── *_routes.py  # API routes
├── bootstrap.py       # App initialization
└── main.py           # Application entry point
tests/                # Test suite
```

## 🛠️ Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
```

### 3. Setup Database

**Option A: PostgreSQL**
```bash
# Start PostgreSQL, then run migrations
alembic upgrade head
```

**Option B: SQLite (Development)**
```bash
# Update .env:
DATABASE_URL=sqlite+aiosqlite:///./app.db

# Run migrations
alembic upgrade head
```

### 4. Run Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📚 API Documentation

Once running, visit:
- **Interactive Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## 🔍 Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/api/health` | GET | Health check with version info |
| `/api/health/liveness` | GET | K8s liveness probe |
| `/api/health/readiness` | GET | K8s readiness probe (checks DB/Redis) |
| `/api/v1/users` | GET | List all users |
| `/api/v1/users` | POST | Create new user |
| `/api/v1/logs` | GET | Query logs with filters |
| `/api/v1/logs/stats` | GET | Log file statistics |

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only

# Run specific file
pytest tests/test_user_service.py
```

## 📋 Database Migrations (Alembic)

```bash
# Initialize Alembic (already done)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🔧 Configuration

Environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | FastAPI-Pro |
| `DEBUG` | Debug mode | false |
| `DATABASE_URL` | Database connection string | Required |
| `REDIS_ENABLED` | Enable Redis caching | false |
| `REDIS_URL` | Redis connection string | - |
| `LOG_LEVEL` | Logging level | INFO |
| `LOG_DIR` | Log directory | logs |

## 🏗️ Architecture Patterns

### Repository Pattern
Data access is abstracted through repositories.

### Service Layer
Business logic is encapsulated in services.

### Dependency Injection
Dependencies are injected via FastAPI's `Depends()`.

### Custom Exceptions
Structured exceptions with automatic error responses.

## 📊 Logging

- **Request ID Tracking** - Every request gets unique ID
- **Performance Metrics** - Response times logged
- **JSON Format** - Machine-readable logs
- **Log Rotation** - Daily rotation with 30-day retention
- **Query API** - Search logs via `/api/v1/logs`

## 🛡️ Error Handling

All errors return consistent JSON:

```json
{
  "error": true,
  "message": "Error description",
  "details": {},
  "path": "/api/v1/endpoint"
}
```

## 🤖 Created With AI

This project was created with the assistance of various AI tools and large language models (LLMs).

## 📝 License

MIT License

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests
4. Submit pull request
