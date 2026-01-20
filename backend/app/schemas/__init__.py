"""Pydantic schemas for API request/response validation."""

from .product import (
    ProductBase,
    ProductCreate,
    ProductResponse,
    ProductListResponse,
    ProductDetailResponse,
)
from .category import (
    CategoryBase,
    CategoryCreate,
    CategoryResponse,
    CategoryWithProducts,
)
from .list import (
    ListItemBase,
    ListItemCreate,
    ListItemResponse,
    UserListBase,
    UserListCreate,
    UserListResponse,
    UserListDetailResponse,
)
from .search import (
    SearchRequest,
    SearchResponse,
    SearchResult,
    SearchSuggestion,
)
from .session import (
    SessionCreate,
    SessionResponse,
)
from .analytics import (
    AnalyticsEventCreate,
    AnalyticsEventResponse,
    AnalyticsBatchCreate,
)

__all__ = [
    # Product
    "ProductBase",
    "ProductCreate",
    "ProductResponse",
    "ProductListResponse",
    "ProductDetailResponse",
    # Category
    "CategoryBase",
    "CategoryCreate",
    "CategoryResponse",
    "CategoryWithProducts",
    # List
    "ListItemBase",
    "ListItemCreate",
    "ListItemResponse",
    "UserListBase",
    "UserListCreate",
    "UserListResponse",
    "UserListDetailResponse",
    # Search
    "SearchRequest",
    "SearchResponse",
    "SearchResult",
    "SearchSuggestion",
    # Session
    "SessionCreate",
    "SessionResponse",
    # Analytics
    "AnalyticsEventCreate",
    "AnalyticsEventResponse",
    "AnalyticsBatchCreate",
]
