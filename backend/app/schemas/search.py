"""Pydantic schemas for Search API."""

from typing import Optional

from pydantic import BaseModel, Field

from .product import ProductResponse


class SearchRequest(BaseModel):
    """Schema for search request."""

    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    category_id: Optional[int] = Field(None, description="Filter by category ID")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price filter")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price filter")
    attributes: Optional[dict] = Field(None, description="Attribute filters")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


class SearchResult(BaseModel):
    """Schema for individual search result with relevance score."""

    product: ProductResponse
    score: float = Field(..., description="Relevance score (0-1)")
    highlights: Optional[dict[str, str]] = Field(
        None, description="Highlighted matching text"
    )


class SearchGrouping(BaseModel):
    """Schema for grouped search results."""

    group_name: str = Field(..., description="Group name (e.g., category)")
    results: list[SearchResult]
    total_in_group: int


class SearchResponse(BaseModel):
    """Schema for search response."""

    query: str
    results: list[SearchResult]
    groupings: Optional[list[SearchGrouping]] = None
    total: int
    page: int
    page_size: int
    pages: int
    best_match: Optional[SearchResult] = Field(
        None, description="AI-curated best match with explanation"
    )
    best_match_reason: Optional[str] = Field(
        None, description="Explanation for best match selection"
    )


class SearchSuggestion(BaseModel):
    """Schema for search suggestion."""

    text: str = Field(..., description="Suggestion text")
    type: str = Field(
        ..., description="Suggestion type: query, category, product, attribute"
    )
    metadata: Optional[dict] = Field(None, description="Additional metadata")


class SearchSuggestionsResponse(BaseModel):
    """Schema for search suggestions response."""

    suggestions: list[SearchSuggestion]
    recent_searches: list[str] = Field(default_factory=list)
    popular_searches: list[str] = Field(default_factory=list)


class FilterOption(BaseModel):
    """Schema for a single filter option."""

    value: str
    label: str
    count: int = Field(..., description="Number of products with this value")


class FilterFacet(BaseModel):
    """Schema for a filter facet (group of options)."""

    name: str = Field(..., description="Filter name (e.g., 'material', 'size')")
    display_name: str = Field(..., description="Human-readable name")
    type: str = Field(
        ..., description="Filter type: checkbox, range, single_select"
    )
    options: list[FilterOption]


class SearchFiltersResponse(BaseModel):
    """Schema for available search filters."""

    facets: list[FilterFacet]
    price_range: Optional[dict[str, float]] = Field(
        None, description="Min/max price in results"
    )
    categories: list["CategoryResponse"] = []


# Import here to avoid circular imports
from .category import CategoryResponse

SearchFiltersResponse.model_rebuild()
