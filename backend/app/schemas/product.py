"""Pydantic schemas for Product API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    """Base product schema with common fields."""

    sku: str = Field(..., min_length=1, max_length=50, description="Product SKU")
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    description: Optional[str] = Field(None, description="Full product description")
    short_description: Optional[str] = Field(
        None, max_length=500, description="Short description for listings"
    )
    price: float = Field(..., gt=0, description="Product price")
    image_url: Optional[str] = Field(None, max_length=500, description="Main image URL")
    thumbnail_url: Optional[str] = Field(None, max_length=500, description="Thumbnail URL")
    attributes: Optional[dict] = Field(default_factory=dict, description="Product attributes")
    specifications: Optional[dict] = Field(default_factory=dict, description="Technical specs")


class ProductCreate(ProductBase):
    """Schema for creating a new product."""

    is_active: bool = Field(default=True)
    is_featured: bool = Field(default=False)
    category_ids: Optional[list[int]] = Field(default=None, description="Category IDs")


class ProductUpdate(BaseModel):
    """Schema for updating a product (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    image_url: Optional[str] = Field(None, max_length=500)
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    attributes: Optional[dict] = None
    specifications: Optional[dict] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    category_ids: Optional[list[int]] = None


class ProductResponse(BaseModel):
    """Schema for product response in listings."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    name: str
    short_description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_active: bool
    is_featured: bool


class ProductDetailResponse(ProductResponse):
    """Schema for detailed product response."""

    description: Optional[str] = None
    attributes: Optional[dict] = None
    specifications: Optional[dict] = None
    categories: list["CategoryResponse"] = []
    created_at: datetime
    updated_at: datetime


class ProductListResponse(BaseModel):
    """Schema for paginated product list response."""

    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
    pages: int


# Import here to avoid circular imports
from .category import CategoryResponse

ProductDetailResponse.model_rebuild()
