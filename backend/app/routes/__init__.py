"""API routes package.

This package contains FastAPI route handlers organized by domain.
"""

from . import admin, analytics, categories, lists, products, search
from .admin import router as admin_router

__all__ = [
    "admin",
    "admin_router",
    "analytics",
    "categories",
    "lists",
    "products",
    "search",
]
