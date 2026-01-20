"""FastAPI dependency injection module."""

from .database import get_db

__all__ = ["get_db"]
