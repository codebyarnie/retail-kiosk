"""Pydantic schemas for Category API."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    """Base category schema with common fields."""

    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    slug: str = Field(..., min_length=1, max_length=100, description="URL-friendly slug")
    description: Optional[str] = Field(None, description="Category description")
    image_url: Optional[str] = Field(None, max_length=500, description="Category image URL")
    display_order: int = Field(default=0, description="Display order for sorting")


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""

    parent_id: Optional[int] = Field(None, description="Parent category ID for hierarchy")
    is_active: bool = Field(default=True)


class CategoryUpdate(BaseModel):
    """Schema for updating a category (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)
    parent_id: Optional[int] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryResponse(BaseModel):
    """Schema for category response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    parent_id: Optional[int] = None
    display_order: int
    is_active: bool


class CategoryTreeResponse(CategoryResponse):
    """Schema for category with children (tree structure)."""

    children: list["CategoryTreeResponse"] = []


class CategoryWithProducts(CategoryResponse):
    """Schema for category with its products."""

    products: list["ProductResponse"] = []
    product_count: int = 0


# Rebuild for forward references
CategoryTreeResponse.model_rebuild()

# Import here to avoid circular imports
from .product import ProductResponse

CategoryWithProducts.model_rebuild()
