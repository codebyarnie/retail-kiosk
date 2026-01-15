.PHONY: help up down restart logs clean install test lint format dev backend-dev frontend-dev worker-dev db-migrate db-seed

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

##@ General

help: ## Display this help message
	@echo "$(BLUE)Retail Kiosk - Development Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(YELLOW)<target>$(NC)\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

clean: ## Clean all build artifacts and caches
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	rm -rf backend/__pycache__ backend/**/__pycache__ backend/.pytest_cache
	rm -rf worker/__pycache__ worker/**/__pycache__
	rm -rf frontend/dist frontend/node_modules/.cache
	rm -rf .mypy_cache .ruff_cache
	@echo "$(GREEN)✓ Clean complete$(NC)"

##@ Docker Services

up: ## Start all services with docker-compose
	@echo "$(BLUE)Starting all services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Services started$(NC)"

down: ## Stop all services
	@echo "$(YELLOW)Stopping all services...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

restart: down up ## Restart all services

logs: ## View logs from all services
	docker-compose logs -f

logs-db: ## View PostgreSQL logs
	docker-compose logs -f postgres

logs-redis: ## View Redis logs
	docker-compose logs -f redis

logs-qdrant: ## View Qdrant logs
	docker-compose logs -f qdrant

ps: ## Show status of all services
	docker-compose ps

##@ Installation

install: install-backend install-frontend install-worker ## Install all dependencies

install-backend: ## Install backend dependencies
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	cd backend && pip install -r requirements.txt
	@echo "$(GREEN)✓ Backend dependencies installed$(NC)"

install-frontend: ## Install frontend dependencies
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	cd frontend && npm install
	@echo "$(GREEN)✓ Frontend dependencies installed$(NC)"

install-worker: ## Install worker dependencies
	@echo "$(BLUE)Installing worker dependencies...$(NC)"
	cd worker && pip install -r requirements.txt
	@echo "$(GREEN)✓ Worker dependencies installed$(NC)"

##@ Development

dev: ## Start all services in development mode (requires separate terminals)
	@echo "$(BLUE)Starting development environment...$(NC)"
	@echo "$(YELLOW)Note: Run 'make backend-dev', 'make frontend-dev', and 'make worker-dev' in separate terminals$(NC)"
	@make up

backend-dev: ## Run backend development server
	@echo "$(BLUE)Starting backend development server...$(NC)"
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend-dev: ## Run frontend development server
	@echo "$(BLUE)Starting frontend development server...$(NC)"
	cd frontend && npm run dev

worker-dev: ## Run Celery worker in development mode
	@echo "$(BLUE)Starting Celery worker...$(NC)"
	cd worker && celery -A celery_app worker --loglevel=info

##@ Testing

test: test-backend ## Run all tests

test-backend: ## Run backend tests
	@echo "$(BLUE)Running backend tests...$(NC)"
	cd backend && pytest

test-frontend: ## Run frontend tests
	@echo "$(BLUE)Running frontend tests...$(NC)"
	cd frontend && npm test

test-watch: ## Run backend tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	cd backend && pytest-watch

##@ Code Quality

lint: lint-backend lint-frontend ## Run all linters

lint-backend: ## Lint backend code
	@echo "$(BLUE)Linting backend code...$(NC)"
	cd backend && ruff check .
	cd backend && mypy .

lint-frontend: ## Lint frontend code
	@echo "$(BLUE)Linting frontend code...$(NC)"
	cd frontend && npm run lint

format: format-backend format-frontend ## Format all code

format-backend: ## Format backend code
	@echo "$(BLUE)Formatting backend code...$(NC)"
	cd backend && ruff format .
	cd backend && ruff check --fix .

format-frontend: ## Format frontend code
	@echo "$(BLUE)Formatting frontend code...$(NC)"
	cd frontend && npm run format

##@ Database

db-migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	cd backend && alembic upgrade head
	@echo "$(GREEN)✓ Migrations complete$(NC)"

db-rollback: ## Rollback last database migration
	@echo "$(YELLOW)Rolling back last migration...$(NC)"
	cd backend && alembic downgrade -1

db-seed: ## Seed database with sample data
	@echo "$(BLUE)Seeding database...$(NC)"
	cd backend && python -m app.scripts.seed_data
	@echo "$(GREEN)✓ Database seeded$(NC)"

db-reset: down ## Reset database (WARNING: deletes all data)
	@echo "$(RED)Resetting database (this will delete all data)...$(NC)"
	docker volume rm retail-kiosk_postgres_data || true
	@make up
	@sleep 5
	@make db-migrate
	@make db-seed
	@echo "$(GREEN)✓ Database reset complete$(NC)"

##@ Build

build: build-backend build-frontend ## Build all services

build-backend: ## Build backend Docker image
	@echo "$(BLUE)Building backend image...$(NC)"
	docker build -t retail-kiosk-backend:latest backend/
	@echo "$(GREEN)✓ Backend image built$(NC)"

build-frontend: ## Build frontend for production
	@echo "$(BLUE)Building frontend...$(NC)"
	cd frontend && npm run build
	@echo "$(GREEN)✓ Frontend built$(NC)"

build-worker: ## Build worker Docker image
	@echo "$(BLUE)Building worker image...$(NC)"
	docker build -t retail-kiosk-worker:latest worker/
	@echo "$(GREEN)✓ Worker image built$(NC)"

##@ Utilities

shell-backend: ## Open a shell in backend container
	docker-compose exec backend bash

shell-db: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U postgres -d retail_kiosk

shell-redis: ## Open Redis CLI
	docker-compose exec redis redis-cli

check: ## Check all services health
	@echo "$(BLUE)Checking services health...$(NC)"
	@docker-compose ps
	@echo ""
	@echo "$(BLUE)PostgreSQL:$(NC)"
	@docker-compose exec -T postgres pg_isready -U postgres || echo "$(RED)✗ PostgreSQL not ready$(NC)"
	@echo "$(BLUE)Redis:$(NC)"
	@docker-compose exec -T redis redis-cli ping || echo "$(RED)✗ Redis not ready$(NC)"
	@echo "$(BLUE)Qdrant:$(NC)"
	@curl -sf http://localhost:6333/healthz > /dev/null && echo "$(GREEN)✓ Qdrant ready$(NC)" || echo "$(RED)✗ Qdrant not ready$(NC)"
