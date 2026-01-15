"""
Configuration module for the Retail Kiosk backend service.

This module uses Pydantic Settings to manage environment variables and
application configuration. It provides type-safe access to all configuration
parameters needed by the application.
"""

from functools import lru_cache
from typing import Any

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via environment variables with the prefix
    'RETAIL_KIOSK_'. For example, DATABASE_URL can be set via
    RETAIL_KIOSK_DATABASE_URL environment variable.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="RETAIL_KIOSK_",
        case_sensitive=False,
        extra="ignore",
    )

    # Application Settings
    app_name: str = Field(default="Retail Kiosk API", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode flag")
    environment: str = Field(
        default="development",
        description="Environment (development, staging, production)",
    )

    # API Settings
    api_host: str = Field(default="0.0.0.0", description="API host address")
    api_port: int = Field(default=8000, description="API port number")
    api_prefix: str = Field(default="/api", description="API route prefix")
    api_workers: int = Field(default=1, description="Number of Uvicorn workers")

    # CORS Settings
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="Allowed CORS origins",
    )
    cors_allow_credentials: bool = Field(
        default=True,
        description="Allow credentials in CORS requests",
    )
    cors_allow_methods: list[str] = Field(
        default=["*"],
        description="Allowed HTTP methods for CORS",
    )
    cors_allow_headers: list[str] = Field(
        default=["*"],
        description="Allowed headers for CORS",
    )

    # Database Settings
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/retail_kiosk",
        description="PostgreSQL database URL for async connections",
    )
    database_pool_size: int = Field(
        default=10,
        description="Database connection pool size",
    )
    database_max_overflow: int = Field(
        default=20,
        description="Maximum number of overflow connections",
    )
    database_pool_timeout: int = Field(
        default=30,
        description="Pool connection timeout in seconds",
    )
    database_echo: bool = Field(
        default=False,
        description="Echo SQL queries (useful for debugging)",
    )

    # Redis Settings
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )
    redis_max_connections: int = Field(
        default=50,
        description="Maximum Redis connection pool size",
    )
    redis_socket_timeout: int = Field(
        default=5,
        description="Redis socket timeout in seconds",
    )
    redis_socket_connect_timeout: int = Field(
        default=5,
        description="Redis socket connect timeout in seconds",
    )

    # Celery Settings
    celery_broker_url: str = Field(
        default="redis://localhost:6379/1",
        description="Celery broker URL",
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/2",
        description="Celery result backend URL",
    )
    celery_task_serializer: str = Field(
        default="json",
        description="Celery task serialization format",
    )
    celery_result_serializer: str = Field(
        default="json",
        description="Celery result serialization format",
    )
    celery_accept_content: list[str] = Field(
        default=["json"],
        description="Accepted content types for Celery",
    )
    celery_timezone: str = Field(
        default="UTC",
        description="Celery timezone",
    )

    # Qdrant Settings
    qdrant_host: str = Field(
        default="localhost",
        description="Qdrant vector database host",
    )
    qdrant_port: int = Field(
        default=6333,
        description="Qdrant HTTP API port",
    )
    qdrant_grpc_port: int = Field(
        default=6334,
        description="Qdrant gRPC port",
    )
    qdrant_api_key: str | None = Field(
        default=None,
        description="Qdrant API key for authentication (optional)",
    )
    qdrant_prefer_grpc: bool = Field(
        default=False,
        description="Prefer gRPC over HTTP for Qdrant connections",
    )

    # Security Settings
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for JWT and encryption",
    )
    algorithm: str = Field(
        default="HS256",
        description="JWT encoding algorithm",
    )
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration time in minutes",
    )
    refresh_token_expire_days: int = Field(
        default=7,
        description="Refresh token expiration time in days",
    )

    # Logging Settings
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    log_format: str = Field(
        default="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        description="Loguru log format",
    )
    log_rotation: str = Field(
        default="500 MB",
        description="Log file rotation size",
    )
    log_retention: str = Field(
        default="10 days",
        description="Log file retention period",
    )

    # Feature Flags
    enable_docs: bool = Field(
        default=True,
        description="Enable API documentation endpoints",
    )
    enable_metrics: bool = Field(
        default=True,
        description="Enable Prometheus metrics endpoint",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("cors_allow_methods", mode="before")
    @classmethod
    def parse_cors_methods(cls, v: Any) -> list[str]:
        """Parse CORS methods from string or list."""
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v

    @field_validator("cors_allow_headers", mode="before")
    @classmethod
    def parse_cors_headers(cls, v: Any) -> list[str]:
        """Parse CORS headers from string or list."""
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v

    @field_validator("celery_accept_content", mode="before")
    @classmethod
    def parse_celery_accept_content(cls, v: Any) -> list[str]:
        """Parse Celery accept content from string or list."""
        if isinstance(v, str):
            return [content.strip() for content in v.split(",")]
        return v

    @property
    def qdrant_url(self) -> str:
        """Get Qdrant URL for HTTP connections."""
        return f"http://{self.qdrant_host}:{self.qdrant_port}"

    @property
    def database_sync_url(self) -> str:
        """Get synchronous database URL (for Alembic migrations)."""
        return self.database_url.replace("+asyncpg", "")

    def get_database_url(self, async_driver: bool = True) -> str:
        """
        Get database URL with appropriate driver.

        Args:
            async_driver: If True, returns async URL; otherwise returns sync URL

        Returns:
            str: Database connection URL
        """
        return self.database_url if async_driver else self.database_sync_url


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    This function uses lru_cache to ensure only one Settings instance
    is created during the application lifecycle, improving performance.

    Returns:
        Settings: Application settings instance
    """
    return Settings()


# Convenience variable for importing settings
settings = get_settings()
