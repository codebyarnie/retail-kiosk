"""Product service for business logic."""

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Category, Product, ProductCategory
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    """Service for product-related business logic."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the product service."""
        self.db = db

    async def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID."""
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.categories))
            .where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    async def get_product_by_sku(self, sku: str) -> Optional[Product]:
        """Get product by SKU."""
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.categories))
            .where(Product.sku == sku)
        )
        return result.scalar_one_or_none()

    async def list_products(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        active_only: bool = True,
        category_id: Optional[int] = None,
        featured_only: bool = False,
    ) -> tuple[list[Product], int]:
        """
        List products with pagination and filtering.

        Returns:
            Tuple of (products list, total count)
        """
        # Build base query
        query = select(Product)

        if active_only:
            query = query.where(Product.is_active == True)

        if featured_only:
            query = query.where(Product.is_featured == True)

        if category_id:
            query = query.join(ProductCategory).where(
                ProductCategory.category_id == category_id
            )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(Product.name)
        result = await self.db.execute(query)
        products = list(result.scalars().all())

        return products, total

    async def create_product(self, product_data: ProductCreate) -> Product:
        """Create a new product."""
        # Extract category IDs if provided
        category_ids = product_data.category_ids
        product_dict = product_data.model_dump(exclude={"category_ids"})

        product = Product(**product_dict)
        self.db.add(product)
        await self.db.flush()

        # Add category associations
        if category_ids:
            for cat_id in category_ids:
                assoc = ProductCategory(product_id=product.id, category_id=cat_id)
                self.db.add(assoc)

        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def update_product(
        self, product_id: int, product_data: ProductUpdate
    ) -> Optional[Product]:
        """Update an existing product."""
        product = await self.get_product_by_id(product_id)
        if not product:
            return None

        # Extract category IDs if provided
        category_ids = product_data.category_ids
        update_data = product_data.model_dump(exclude={"category_ids"}, exclude_unset=True)

        for field, value in update_data.items():
            setattr(product, field, value)

        # Update categories if provided
        if category_ids is not None:
            # Remove existing associations
            await self.db.execute(
                ProductCategory.__table__.delete().where(
                    ProductCategory.product_id == product_id
                )
            )
            # Add new associations
            for cat_id in category_ids:
                assoc = ProductCategory(product_id=product_id, category_id=cat_id)
                self.db.add(assoc)

        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def delete_product(self, product_id: int) -> bool:
        """Delete a product (soft delete by setting is_active=False)."""
        product = await self.get_product_by_id(product_id)
        if not product:
            return False

        product.is_active = False
        await self.db.commit()
        return True

    async def get_featured_products(self, limit: int = 10) -> list[Product]:
        """Get featured products for homepage."""
        result = await self.db.execute(
            select(Product)
            .where(Product.is_active == True, Product.is_featured == True)
            .limit(limit)
            .order_by(Product.name)
        )
        return list(result.scalars().all())
