# Retail Kiosk

A modern, scalable retail kiosk application built with FastAPI, React, and Celery. This system provides an intuitive self-service interface for customers with powerful backend processing and real-time capabilities.

## 🚀 Features

- **Modern Frontend**: React + TypeScript + Vite for fast, responsive UI
- **Robust Backend**: FastAPI with async support for high performance
- **Background Processing**: Celery workers for async task handling
- **Vector Search**: Qdrant integration for semantic search capabilities
- **Real-time Caching**: Redis for session management and caching
- **Persistent Storage**: PostgreSQL for reliable data persistence
- **Containerized**: Docker Compose for easy deployment
- **Developer Tools**: Comprehensive Makefile commands for development workflow

## 🏗️ Architecture

The Retail Kiosk application follows a modern microservices architecture:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│  Database   │
│  React/TS   │     │   FastAPI   │     │ PostgreSQL  │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ├────────────▶ Redis (Cache)
                           │
                           └────────────▶ Qdrant (Vector DB)
                           │
                    ┌──────┴──────┐
                    │   Worker    │
                    │   Celery    │
                    └─────────────┘
```

### Components

- **Frontend**: React-based SPA with TypeScript for type safety
- **Backend**: FastAPI REST API with async endpoints
- **Worker**: Celery workers for background tasks (inventory sync, analytics, etc.)
- **PostgreSQL**: Primary data store
- **Redis**: Cache and message broker
- **Qdrant**: Vector database for semantic search

## 🛠️ Tech Stack

### Backend
- Python 3.11+
- FastAPI - Modern web framework
- SQLAlchemy - ORM
- Alembic - Database migrations
- Pydantic - Data validation
- Celery - Task queue

### Frontend
- React 18
- TypeScript
- Vite - Build tool
- React Router - Routing
- TanStack Query - Data fetching
- Tailwind CSS - Styling

### Infrastructure
- Docker & Docker Compose
- PostgreSQL 16
- Redis 7
- Qdrant (latest)

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Python** (3.11+)
- **Node.js** (18+) and **npm** (9+)
- **Git**
- **Make** (optional, but recommended)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd retail-kiosk
```

### 2. Start Infrastructure Services

```bash
make up
```

This will start PostgreSQL, Redis, and Qdrant in Docker containers.

### 3. Install Dependencies

```bash
# Install all dependencies (backend, frontend, worker)
make install

# Or install individually
make install-backend
make install-frontend
make install-worker
```

### 4. Run Database Migrations

```bash
make db-migrate
```

### 5. Start Development Servers

Open three separate terminals:

**Terminal 1 - Backend:**
```bash
make backend-dev
# Backend will run at http://localhost:8000
# API docs available at http://localhost:8000/docs
```

**Terminal 2 - Frontend:**
```bash
make frontend-dev
# Frontend will run at http://localhost:5173
```

**Terminal 3 - Worker:**
```bash
make worker-dev
# Celery worker will start processing tasks
```

## 🔧 Development

### Available Make Commands

View all available commands:
```bash
make help
```

#### Docker Services
```bash
make up          # Start all services
make down        # Stop all services
make restart     # Restart all services
make logs        # View logs from all services
make ps          # Show status of all services
make check       # Check all services health
```

#### Installation
```bash
make install              # Install all dependencies
make install-backend      # Install backend dependencies
make install-frontend     # Install frontend dependencies
make install-worker       # Install worker dependencies
```

#### Development
```bash
make dev             # Start development environment
make backend-dev     # Run backend development server
make frontend-dev    # Run frontend development server
make worker-dev      # Run Celery worker
```

#### Testing
```bash
make test            # Run all tests
make test-backend    # Run backend tests
make test-frontend   # Run frontend tests
make test-watch      # Run backend tests in watch mode
```

#### Code Quality
```bash
make lint             # Run all linters
make lint-backend     # Lint backend code
make lint-frontend    # Lint frontend code
make format           # Format all code
make format-backend   # Format backend code
make format-frontend  # Format frontend code
```

#### Database
```bash
make db-migrate     # Run database migrations
make db-rollback    # Rollback last migration
make db-seed        # Seed database with sample data
make db-reset       # Reset database (WARNING: deletes all data)
```

#### Build
```bash
make build            # Build all services
make build-backend    # Build backend Docker image
make build-frontend   # Build frontend for production
make build-worker     # Build worker Docker image
```

#### Utilities
```bash
make shell-backend    # Open a shell in backend container
make shell-db         # Open PostgreSQL shell
make shell-redis      # Open Redis CLI
make clean            # Clean build artifacts and caches
```

## 📁 Project Structure

```
retail-kiosk/
├── backend/                 # FastAPI backend service
│   ├── app/
│   │   ├── models/         # SQLAlchemy models
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── config.py       # Configuration management
│   │   └── main.py         # FastAPI application
│   ├── tests/              # Backend tests
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
│
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   ├── App.tsx        # Root component
│   │   └── main.tsx       # Entry point
│   ├── package.json
│   └── Dockerfile
│
├── worker/                 # Celery worker service
│   ├── tasks.py           # Task definitions
│   ├── celery_app.py      # Celery configuration
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml      # Docker services configuration
├── Makefile               # Development commands
└── README.md              # This file
```

## 🔐 Environment Variables

### Backend (.env)

Create a `backend/.env` file:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/retail_kiosk

# Redis
REDIS_URL=redis://localhost:6379/0

# Qdrant
QDRANT_URL=http://localhost:6333

# Application
DEBUG=True
SECRET_KEY=your-secret-key-here
```

### Frontend (.env)

Create a `frontend/.env` file:

```env
VITE_API_URL=http://localhost:8000
```

### Worker (.env)

Create a `worker/.env` file:

```env
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 🧪 Testing

### Run All Tests

```bash
make test
```

### Backend Tests

```bash
# Run once
make test-backend

# Watch mode
make test-watch
```

### Frontend Tests

```bash
make test-frontend
```

## 🐳 Docker Deployment

### Build All Images

```bash
make build
```

### Run in Production Mode

```bash
docker-compose up -d
```

## 📊 Accessing Services

Once all services are running:

- **Frontend**: http://localhost:5173 (dev) or http://localhost:3000 (prod)
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Qdrant**: http://localhost:6333

## 🔍 Health Checks

Check the health of all services:

```bash
make check
```

Or individually:
```bash
docker-compose ps
curl http://localhost:8000/health      # Backend
curl http://localhost:6333/healthz     # Qdrant
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- **Backend**: Follow PEP 8, use `ruff` and `black` for formatting
- **Frontend**: Follow Airbnb style guide, use Prettier and ESLint
- **Commits**: Use conventional commits format

## 🐛 Troubleshooting

### Port Already in Use

If you encounter port conflicts:

```bash
# Check what's using the port
lsof -i :8000  # Backend
lsof -i :5173  # Frontend
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :6333  # Qdrant
```

### Docker Issues

```bash
# Reset everything
make down
make clean
docker system prune -a

# Restart
make up
```

### Database Connection Issues

```bash
# Reset database
make db-reset
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Development Team** - *Initial work*

## 🙏 Acknowledgments

- FastAPI for the amazing web framework
- React team for the excellent frontend library
- Celery for reliable task processing
- The open-source community

---

**Built with ❤️ for retail excellence**
