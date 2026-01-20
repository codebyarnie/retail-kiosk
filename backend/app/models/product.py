"""Product and Category models for the product catalog."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .list import ListItem


class Category(Base, TimestampMixin):
    """Category model for organizing products."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Self-referential relationship for hierarchical categories
    parent: Mapped[Optional["Category"]] = relationship(
        "Category", remote_side=[id], back_populates="children"
    )
    children: Mapped[list["Category"]] = relationship(
        "Category", back_populates="parent", cascade="all, delete-orphan"
    )

    # Products in this category
    products: Mapped[list["Product"]] = relationship(
        "Product", secondary="product_categories", back_populates="categories"
    )

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, slug='{self.slug}', name='{self.name}')>"


class Product(Base, TimestampMixin):
    """Product model representing items in the catalog."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    short_description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Product attributes stored as JSONB for flexible filtering
    # Example: {"material": "stainless steel", "size": "M8x50", "thread": "coarse"}
    attributes: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, default=dict)

    # Specifications stored as JSONB
    # Example: {"weight": "50g", "dimensions": "50x8x8mm", "color": "silver"}
    specifications: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, default=dict)

    # Flags
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)

    # Vector embedding status
    embedding_updated_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    categories: Mapped[list["Category"]] = relationship(
        "Category", secondary="product_categories", back_populates="products"
    )
    list_items: Mapped[list["ListItem"]] = relationship(
        "ListItem", back_populates="product", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_products_name_search", "name"),
        Index("ix_products_active_featured", "is_active", "is_featured"),
    )

    def __repr__(self) -> str:
        return f"<Product(sku='{self.sku}', name='{self.name}')>"


class ProductCategory(Base):
    """Association table for Product-Category many-to-many relationship."""

    __tablename__ = "product_categories"

    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True
    )
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True
    )

    __table_args__ = (Index("ix_product_categories_category", "category_id"),)
