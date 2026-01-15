"""
Configuration module for the Retail Kiosk worker service.

This module uses Pydantic Settings to manage environment variables and
worker configuration. It provides type-safe access to all configuration
parameters needed by the Celery worker.
"""

from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    """
    Worker settings loaded from environment variables.

    All settings can be overridden via environment variables with the prefix
    'RETAIL_KIOSK_'. For example, CELERY_BROKER_URL can be set via
    RETAIL_KIOSK_CELERY_BROKER_URL environment variable.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="RETAIL_KIOSK_",
        case_sensitive=False,
        extra="ignore",
    )

    # Application Settings
    app_name: str = Field(
        default="Retail Kiosk Worker",
        description="Worker application name",
    )
    app_version: str = Field(default="0.1.0", description="Worker version")
    debug: bool = Field(default=False, description="Debug mode flag")
    environment: str = Field(
        default="development",
        description="Environment (development, staging, production)",
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
    celery_enable_utc: bool = Field(
        default=True,
        description="Enable UTC timezone for Celery",
    )
    celery_task_track_started: bool = Field(
        default=True,
        description="Track task started state",
    )
    celery_task_time_limit: int = Field(
        default=3600,
        description="Hard time limit for tasks in seconds (1 hour)",
    )
    celery_task_soft_time_limit: int = Field(
        default=1800,
        description="Soft time limit for tasks in seconds (30 minutes)",
    )
    celery_worker_prefetch_multiplier: int = Field(
        default=4,
        description="Number of tasks to prefetch per worker",
    )
    celery_worker_max_tasks_per_child: int = Field(
        default=1000,
        description="Maximum tasks before recycling worker process",
    )

    # Redis Settings (for task locking and caching)
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for caching",
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

    # Database Settings (for direct DB access from tasks)
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/retail_kiosk",
        description="PostgreSQL database URL for sync connections",
    )
    database_pool_size: int = Field(
        default=5,
        description="Database connection pool size",
    )
    database_max_overflow: int = Field(
        default=10,
        description="Maximum number of overflow connections",
    )
    database_echo: bool = Field(
        default=False,
        description="Echo SQL queries (useful for debugging)",
    )

    # Qdrant Settings (Vector Database)
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

    # Task-specific Settings
    product_sync_interval: int = Field(
        default=3600,
        description="Product sync interval in seconds (1 hour)",
    )
    image_optimization_quality: int = Field(
        default=85,
        description="Image optimization quality (0-100)",
    )
    max_concurrent_image_tasks: int = Field(
        default=5,
        description="Maximum concurrent image processing tasks",
    )

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

    def get_celery_config(self) -> dict[str, Any]:
        """
        Get Celery configuration dictionary.

        Returns:
            dict: Celery configuration parameters
        """
        return {
            "broker_url": self.celery_broker_url,
            "result_backend": self.celery_result_backend,
            "task_serializer": self.celery_task_serializer,
            "result_serializer": self.celery_result_serializer,
            "accept_content": self.celery_accept_content,
            "timezone": self.celery_timezone,
            "enable_utc": self.celery_enable_utc,
            "task_track_started": self.celery_task_track_started,
            "task_time_limit": self.celery_task_time_limit,
            "task_soft_time_limit": self.celery_task_soft_time_limit,
            "worker_prefetch_multiplier": self.celery_worker_prefetch_multiplier,
            "worker_max_tasks_per_child": self.celery_worker_max_tasks_per_child,
        }


@lru_cache
def get_settings() -> WorkerSettings:
    """
    Get cached worker settings instance.

    This function uses lru_cache to ensure only one WorkerSettings instance
    is created during the application lifecycle, improving performance.

    Returns:
        WorkerSettings: Worker settings instance
    """
    return WorkerSettings()


# Convenience variable for importing settings
settings = get_settings()
