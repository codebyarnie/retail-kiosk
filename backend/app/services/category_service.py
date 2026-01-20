"""Category service for business logic."""

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.strategy_options import _AbstractLoad

from app.models import Category, Product, ProductCategory
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    """Service for category-related business logic."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the category service."""
        self.db = db

    async def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Get category by ID."""
        result = await self.db.execute(
            select(Category)
            .options(selectinload(Category.children))
            .where(Category.id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_category_by_slug(self, slug: str) -> Optional[Category]:
        """Get category by slug."""
        result = await self.db.execute(
            select(Category)
            .options(selectinload(Category.children))
            .where(Category.slug == slug)
        )
        return result.scalar_one_or_none()

    async def list_categories(
        self,
        *,
        active_only: bool = True,
        root_only: bool = False,
    ) -> list[Category]:
        """
        List all categories.

        Args:
            active_only: Only return active categories
            root_only: Only return root-level categories (no parent)
        """
        query = select(Category).options(selectinload(Category.children))

        if active_only:
            query = query.where(Category.is_active == True)

        if root_only:
            query = query.where(Category.parent_id == None)

        query = query.order_by(Category.display_order, Category.name)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_category_tree(self) -> list[Category]:
        """Get full category tree (root categories with nested children)."""
        # Build recursive loading strategy for nested children up to 5 levels deep
        children_load: _AbstractLoad = selectinload(Category.children)
        for _ in range(4):  # Add 4 more levels (total 5 levels)
            children_load = children_load.selectinload(Category.children)

        query = (
            select(Category)
            .options(children_load)
            .where(Category.is_active == True, Category.parent_id == None)
            .order_by(Category.display_order, Category.name)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_category_with_products(
        self,
        category_id: int,
        *,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[Optional[Category], list[Product], int]:
        """
        Get category with its products.

        Returns:
            Tuple of (category, products list, total product count)
        """
        category = await self.get_category_by_id(category_id)
        if not category:
            return None, [], 0

        # Get products in this category
        query = (
            select(Product)
            .join(ProductCategory)
            .where(
                ProductCategory.category_id == category_id,
                Product.is_active == True,
            )
        )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(Product.name)
        result = await self.db.execute(query)
        products = list(result.scalars().all())

        return category, products, total

    async def create_category(self, category_data: CategoryCreate) -> Category:
        """Create a new category."""
        category = Category(**category_data.model_dump())
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def update_category(
        self, category_id: int, category_data: CategoryUpdate
    ) -> Optional[Category]:
        """Update an existing category."""
        category = await self.get_category_by_id(category_id)
        if not category:
            return None

        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def delete_category(self, category_id: int) -> bool:
        """Delete a category (soft delete by setting is_active=False)."""
        category = await self.get_category_by_id(category_id)
        if not category:
            return False

        category.is_active = False
        await self.db.commit()
        return True

    async def get_product_count(self, category_id: int) -> int:
        """Get the number of products in a category."""
        result = await self.db.execute(
            select(func.count())
            .select_from(ProductCategory)
            .where(ProductCategory.category_id == category_id)
        )
        return result.scalar() or 0
