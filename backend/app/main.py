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


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager for startup and shutdown events.

    This handles initialization and cleanup of database connections,
    Redis connections, and other resources.
    """
    # Startup: Initialize connections and resources
    # TODO: Initialize database connection pool
    # TODO: Initialize Redis connection
    # TODO: Initialize Qdrant client
    yield
    # Shutdown: Clean up connections and resources
    # TODO: Close database connections
    # TODO: Close Redis connections
    # TODO: Close Qdrant client


# Create FastAPI application instance
app = FastAPI(
    title="Retail Kiosk API",
    description="Backend service for the Retail Kiosk application",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite and common dev ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
            "version": "0.1.0",
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
        "version": "0.1.0",
        "docs": "/api/docs",
        "health": "/health",
    }


# TODO: Include routers from app.routes
# Example:
# from app.routes import products, inventory, transactions
# app.include_router(products.router, prefix="/api/products", tags=["Products"])
# app.include_router(inventory.router, prefix="/api/inventory", tags=["Inventory"])
# app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])
