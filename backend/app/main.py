"""
FastAPI main application entry point.

This module initializes the FastAPI application with middleware,
routers, and lifecycle events for the Retail Kiosk backend service.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.config import settings
from app.dependencies.database import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager for startup and shutdown events.

    This handles initialization and cleanup of database connections,
    Redis connections, and other resources.
    """
    # Startup: Initialize connections and resources
    logger.info("Starting up Retail Kiosk API...")

    # Initialize database connection pool
    try:
        await init_db()
        logger.info("Database connection pool initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    yield

    # Shutdown: Clean up connections and resources
    logger.info("Shutting down Retail Kiosk API...")

    # Close database connections
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI application instance
app = FastAPI(
    title=settings.app_name,
    description="Backend service for the Retail Kiosk application",
    version=settings.app_version,
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url="/redoc" if settings.enable_docs else None,
    openapi_url="/openapi.json" if settings.enable_docs else None,
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> JSONResponse:
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        JSONResponse: Service status and version information
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "retail-kiosk-backend",
            "version": settings.app_version,
            "environment": settings.environment,
        },
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """
    Root endpoint providing API information.

    Returns:
        dict: Basic API information and documentation links
    """
    return {
        "message": "Retail Kiosk API",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }


# Import and include routers
from app.routes import admin_router, analytics, categories, lists, products, search

app.include_router(products.router, prefix="/api", tags=["Products"])
app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(lists.router, prefix="/api", tags=["Lists"])
app.include_router(categories.router, prefix="/api", tags=["Categories"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])
app.include_router(admin_router, prefix="/api")
