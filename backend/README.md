# Backend Service

FastAPI-based REST API server for the Retail Kiosk application.

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- PostgreSQL 16+ (for production/development)
- Redis 7+ (for caching and Celery broker)
- Qdrant (for vector database operations)

## Installation

### Quick Installation (Recommended)

Run the provided installation script:

**Linux/macOS:**
```bash
cd backend
bash install_and_verify.sh
```

**Windows:**
```cmd
cd backend
install_and_verify.bat
```

The script will:
1. Check Python version (requires 3.11+)
2. Upgrade pip, setuptools, and wheel
3. Install all dependencies from requirements.txt
4. Run verification checks to ensure everything is working

### Manual Installation

If you prefer to install manually:

```bash
cd backend

# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt

# Verify installation
python verify_installation.py
```

### Verify Installation Only

If dependencies are already installed and you just want to verify:

```bash
cd backend
python verify_installation.py
```

Expected output:
```
Backend imports OK
```

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and configure the following:
   - `RETAIL_KIOSK_DATABASE_URL`: PostgreSQL connection string
   - `RETAIL_KIOSK_REDIS_URL`: Redis connection string
   - `RETAIL_KIOSK_SECRET_KEY`: JWT secret key (generate a secure random string)
   - Other settings as needed

## Running the Development Server

Start the FastAPI development server with auto-reload:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- Health check: http://localhost:8000/health

## Project Structure

```
backend/
├── app/
│   ├── __init__.py          # Application package
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── models/              # SQLAlchemy models
│   ├── routes/              # API route handlers
│   └── services/            # Business logic services
├── tests/                   # Test suite
│   └── __init__.py
├── .dockerignore            # Docker build exclusions
├── .env.example             # Example environment variables
├── .ruff.toml               # Ruff linter configuration
├── Dockerfile               # Container image definition
├── mypy.ini                 # MyPy type checker configuration
├── pyproject.toml           # Project metadata and tool configs
├── pytest.ini               # Pytest configuration
├── requirements.txt         # Python dependencies
├── verify_installation.py   # Installation verification script
├── install_and_verify.sh    # Installation script (Linux/macOS)
└── install_and_verify.bat   # Installation script (Windows)
```

## Development

### Code Quality Tools

The project uses several tools to maintain code quality:

- **Ruff**: Fast Python linter (replaces flake8, pylint, etc.)
- **Black**: Code formatter
- **MyPy**: Static type checker
- **isort**: Import statement organizer

Run all quality checks:

```bash
cd backend

# Linting
ruff check .

# Auto-fix linting issues
ruff check --fix .

# Format code
black .

# Type checking
mypy app/

# Import sorting
isort .
```

### Testing

Run the test suite:

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html --cov-report=term-missing

# Run specific test markers
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Exclude slow tests
```

Test markers:
- `unit`: Fast unit tests
- `integration`: Integration tests requiring services
- `slow`: Slow-running tests
- `api`: API endpoint tests
- `db`: Database tests
- `celery`: Celery task tests
- `redis`: Redis tests
- `qdrant`: Qdrant vector database tests

### Database Migrations

Create and apply database migrations using Alembic:

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

## Docker

### Build the Docker image

```bash
docker build -t retail-kiosk-backend:latest ./backend
```

### Run with Docker Compose

From the project root:

```bash
docker-compose up backend
```

This will start the backend service along with PostgreSQL, Redis, and Qdrant.

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/api/docs
  - Interactive API documentation
  - Test endpoints directly from the browser

- **ReDoc**: http://localhost:8000/api/redoc
  - Clean, readable API documentation

## Dependencies

### Core Framework
- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server with high performance
- **Pydantic**: Data validation and settings management

### Database
- **SQLAlchemy**: SQL toolkit and ORM
- **Alembic**: Database migration tool
- **psycopg2-binary**: PostgreSQL adapter (sync)
- **asyncpg**: PostgreSQL adapter (async)

### Caching & Message Broker
- **Redis**: In-memory data store
- **hiredis**: High-performance Redis protocol parser

### Vector Database
- **qdrant-client**: Client for Qdrant vector database

### Celery Integration
- **Celery**: Distributed task queue

### Authentication & Security
- **python-jose**: JWT token handling
- **passlib**: Password hashing with bcrypt

### Development & Testing
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking support
- **faker**: Fake data generation

### Code Quality
- **ruff**: Fast Python linter
- **black**: Code formatter
- **mypy**: Static type checker
- **isort**: Import statement organizer

## Troubleshooting

### Import Errors

If you get import errors, ensure:
1. You're in the backend directory
2. Dependencies are installed: `pip install -r requirements.txt`
3. Python version is 3.11+: `python --version`

### Database Connection Errors

If you can't connect to the database:
1. Ensure PostgreSQL is running: `docker-compose up postgres`
2. Check DATABASE_URL in your .env file
3. Verify credentials match docker-compose.yml

### Redis Connection Errors

If you can't connect to Redis:
1. Ensure Redis is running: `docker-compose up redis`
2. Check REDIS_URL in your .env file
3. Test connection: `redis-cli ping`

### Port Already in Use

If port 8000 is already in use:
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

## Contributing

1. Follow the existing code style
2. Add tests for new features
3. Run quality checks before committing:
   ```bash
   ruff check . && black . && mypy app/ && pytest
   ```
4. Update documentation as needed

## License

[Add license information here]
