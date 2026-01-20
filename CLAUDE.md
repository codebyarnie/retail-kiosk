# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Retail Kiosk is a self-service product browser for hardware/DIY retail. It's a full-stack microservices app with:
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI + SQLAlchemy 2.0 + Pydantic + asyncpg
- **Worker**: Celery + Redis (background tasks)
- **Databases**: PostgreSQL 16 (primary) + Redis 7 (cache) + Qdrant (vector search)

## Common Commands

### Development Setup
```bash
make up                   # Start Docker services (PostgreSQL, Redis, Qdrant)
make install              # Install all dependencies
make db-migrate           # Run database migrations
```

### Running Services (separate terminals)
```bash
make backend-dev          # FastAPI at http://localhost:8000 (docs at /docs)
make frontend-dev         # Vite at http://localhost:5173
make worker-dev           # Celery worker
```

### Testing
```bash
make test                 # Run all tests
make test-backend         # Backend tests with coverage
make test-frontend        # Frontend tests
pytest backend/tests/test_file.py::test_name  # Single test
```

### Code Quality
```bash
make lint                 # Run all linters
make format               # Auto-format all code
```

### Database
```bash
make db-migrate           # Apply migrations
make db-rollback          # Rollback last migration
alembic revision --autogenerate -m "description"  # Create migration (from backend/)
```

## Architecture

```
Frontend (React SPA) → Backend (FastAPI REST) → PostgreSQL (data)
                                              → Redis (cache + Celery broker)
                                              → Qdrant (vector search)
                                              → Celery Worker (background tasks)
```

### Backend Layering (backend/app/)
- `routes/` - API endpoints (thin, delegate to services)
- `services/` - Business logic
- `models/` - SQLAlchemy ORM models
- `schemas/` - Pydantic request/response validation
- `dependencies/` - FastAPI dependency injection

### Frontend Structure (frontend/src/)
- `components/` - Reusable UI components
- `pages/` - Page components
- `services/` - API clients (Axios)
- `stores/` - Zustand state management
- `hooks/` - Custom React hooks
- `types/` - TypeScript definitions

## Code Patterns

### Backend
- **Async everywhere**: Use `async/await` for all database operations
- **Pydantic validation**: All API inputs/outputs use Pydantic schemas
- **Service layer**: Business logic lives in services, not routes
- **Type hints required**: All function signatures must have type hints

```python
# Route pattern
@router.get("/products/{sku}", response_model=ProductResponse)
async def get_product(sku: str, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    product = await service.get_product_by_sku(sku)
    if not product:
        raise HTTPException(status_code=404, detail="Not found")
    return product
```

### Frontend
- **TypeScript strict mode**: No `any` types
- **Zustand for global state**: Server state via TanStack Query
- **Tailwind for styling**: Utility-first CSS

## Code Style

### Python
- Line length: 100 chars
- Formatter: Black + Ruff
- Type checker: mypy (strict)
- Docstrings: Google style

### TypeScript
- Line length: 80 chars
- Formatter: Prettier
- Linter: ESLint with TypeScript plugin
- Quotes: Single quotes

## Git Conventions

Branch naming: `feature/description`, `bugfix/description`, `hotfix/description`

Commit format (conventional commits):
```
feat(scope): add product search
fix(api): handle null descriptions
```

Pre-commit hooks enforce formatting, linting, and type checking.

## Key Service Endpoints

- Backend API: http://localhost:8000/api
- Swagger docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432 (postgres:postgres)
- Redis: localhost:6379
- Qdrant: http://localhost:6333

use context7

## Nothing is Done Until Tested

**Before marking any work complete:**

1. **Test it** - Use Playwright for UI changes, unit tests for logic
2. **Tests must pass** - Do not proceed until green
3. **Never delete failing tests** - Fix the code, not the test
4. **Deploy to verify** - Run in Docker to confirm it works

**The cycle:**
```
Code -> Test -> Fix -> Test -> Deploy -> Verify -> Done
```

If tests fail, the work is not done. Period.

## Mandatory Development Practices

### 1. Deployment
- **Always use Docker** for deployment and testing
- Use docker-compose up -d to start services
- Verify services are healthy before testing

### 2. Documentation Lookup
- **Use Context7** (via MCP tool) to look up current documentation for any libraries or frameworks
- Always query Context7 before implementing features that depend on external libraries
- This ensures you have up-to-date API references and examples

### 3. UI Testing
- **Use Playwright** to test all UI components after development
- Write E2E tests for new features
- Run npx playwright test to verify UI functionality
- Test in the Docker environment to match production

## IMPORTANT: Tool Availability

If any of these tools are unavailable, **immediately alert the user**:
- **Context7 not available?** - I cant access Context7 MCP tool - I need it to look up current documentation!
- **Docker not running?** - Docker isnt available - I need it to deploy and test properly!
- **Playwright not working?** - Playwright isnt accessible - I cant verify the UI components!

Do NOT silently work around missing tools. These are mandatory, not optional.


Find a TODO.md and start working on it! Mark tasks as done when they are complete.
If you do not find a TODO.md you should find specifications in docs/ and doc/, break down these into tasks into the TODO.md file.

never deploy directly, always use docker-compose up -d to start services, verify services are healthy before testing, use context7 to look up current documentation for any libraries or frameworks, always query context7 before implementing features that depend on external libraries, this ensures you have up-to-date api references and examples, use playwright to test all ui components after development, write e2e tests for new features, run npx playwright test to verify ui functionality, test in the docker environment. Even unit tests should be executed in docker.