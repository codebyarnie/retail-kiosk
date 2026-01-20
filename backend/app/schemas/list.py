"""Pydantic schemas for User List API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ListItemBase(BaseModel):
    """Base list item schema."""

    product_sku: str = Field(..., description="Product SKU to add")
    quantity: int = Field(default=1, ge=1, le=999, description="Quantity")
    notes: Optional[str] = Field(None, max_length=500, description="Item notes")


class ListItemCreate(ListItemBase):
    """Schema for adding an item to a list."""

    pass


class ListItemUpdate(BaseModel):
    """Schema for updating a list item."""

    quantity: Optional[int] = Field(None, ge=1, le=999)
    notes: Optional[str] = Field(None, max_length=500)


class ListItemResponse(BaseModel):
    """Schema for list item response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    quantity: int
    notes: Optional[str] = None
    price_at_add: Optional[float] = None
    product: "ProductResponse"
    created_at: datetime


class UserListBase(BaseModel):
    """Base user list schema."""

    name: str = Field(default="My List", min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class UserListCreate(UserListBase):
    """Schema for creating a new list."""

    pass


class UserListUpdate(BaseModel):
    """Schema for updating a list."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class UserListResponse(BaseModel):
    """Schema for list response (summary)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    list_id: str
    name: str
    description: Optional[str] = None
    share_code: Optional[str] = None
    total_items: int = 0
    unique_items: int = 0
    created_at: datetime
    updated_at: datetime


class UserListDetailResponse(UserListResponse):
    """Schema for detailed list response with items."""

    items: list[ListItemResponse] = []


class ListSyncResponse(BaseModel):
    """Schema for QR sync response."""

    list_id: str
    share_code: str
    sync_url: str


# Import here to avoid circular imports
from .product import ProductResponse

ListItemResponse.model_rebuild()
UserListDetailResponse.model_rebuild()
