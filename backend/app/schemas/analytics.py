"""Pydantic schemas for Analytics API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AnalyticsEventCreate(BaseModel):
    """Schema for creating an analytics event."""

    event_type: str = Field(..., max_length=50, description="Event type")
    event_data: Optional[dict] = Field(default_factory=dict, description="Event payload")
    product_sku: Optional[str] = Field(None, max_length=50, description="Related product SKU")
    search_query: Optional[str] = Field(None, max_length=500, description="Related search query")
    timestamp: Optional[datetime] = Field(None, description="Event timestamp (server uses now if not provided)")


class AnalyticsBatchCreate(BaseModel):
    """Schema for creating multiple analytics events at once."""

    events: list[AnalyticsEventCreate] = Field(..., min_length=1, max_length=100)


class AnalyticsEventResponse(BaseModel):
    """Schema for analytics event response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    event_timestamp: datetime
    event_data: Optional[dict] = None
    product_sku: Optional[str] = None
    search_query: Optional[str] = None


class AnalyticsSummary(BaseModel):
    """Schema for analytics summary response."""

    session_id: str
    total_events: int
    searches_performed: int
    products_viewed: int
    items_added_to_list: int
    session_duration_seconds: Optional[int] = None


class PopularSearchesResponse(BaseModel):
    """Schema for popular searches."""

    searches: list[dict] = Field(..., description="List of {query, count} objects")
    period: str = Field(..., description="Time period (e.g., 'last_24h', 'last_7d')")


class TopProductsResponse(BaseModel):
    """Schema for top viewed/added products."""

    products: list[dict] = Field(..., description="List of {sku, name, view_count, add_count}")
    period: str
