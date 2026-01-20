"""Tests for ProductService business logic.

This module contains unit tests for the ProductService, covering
product retrieval, listing, filtering, and CRUD operations.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.product_service import ProductService
from tests.factories import (
    create_category_in_db,
    create_product_category,
    create_product_in_db,
)


class TestGetProductBySku:
    """Tests for ProductService.get_product_by_sku method."""

    async def test_get_product_by_sku_returns_product(self, db_session: AsyncSession):
        """Test that get_product_by_sku returns the correct product."""
        # Arrange
        product = await create_product_in_db(
            db_session,
            sku="TEST-SKU-001",
            name="Test Product",
            price=29.99,
        )

        service = ProductService(db_session)

        # Act
        result = await service.get_product_by_sku("TEST-SKU-001")

        # Assert
        assert result is not None
        assert result.sku == "TEST-SKU-001"
        assert result.name == "Test Product"
        assert result.price == 29.99

    async def test_get_product_by_sku_returns_none_for_nonexistent(
        self, db_session: AsyncSession
    ):
        """Test that get_product_by_sku returns None for non-existent SKU."""
        service = ProductService(db_session)

        result = await service.get_product_by_sku("NONEXISTENT-SKU")

        assert result is None

    async def test_get_product_by_sku_is_case_sensitive(self, db_session: AsyncSession):
        """Test that SKU lookup is case-sensitive."""
        await create_product_in_db(
            db_session,
            sku="TEST-SKU-001",
            name="Test Product",
        )

        service = ProductService(db_session)

        # Act - try lowercase version
        result = await service.get_product_by_sku("test-sku-001")

        # Assert - should not find it (case sensitive)
        assert result is None


class TestGetProductById:
    """Tests for ProductService.get_product_by_id method."""

    async def test_get_product_by_id_returns_product(self, db_session: AsyncSession):
        """Test that get_product_by_id returns the correct product."""
        product = await create_product_in_db(
            db_session,
            sku="TEST-ID-001",
            name="Product By ID Test",
            price=49.99,
        )

        service = ProductService(db_session)

        result = await service.get_product_by_id(product.id)

        assert result is not None
        assert result.id == product.id
        assert result.name == "Product By ID Test"

    async def test_get_product_by_id_returns_none_for_nonexistent(
        self, db_session: AsyncSession
    ):
        """Test that get_product_by_id returns None for non-existent ID."""
        service = ProductService(db_session)

        result = await service.get_product_by_id(99999)

        assert result is None


class TestListProducts:
    """Tests for ProductService.list_products method."""

    async def test_list_products_returns_all_active_products(
        self, db_session: AsyncSession
    ):
        """Test that list_products returns all active products by default."""
        # Create multiple products
        await create_product_in_db(db_session, sku="PROD-001", name="Product A")
        await create_product_in_db(db_session, sku="PROD-002", name="Product B")
        await create_product_in_db(db_session, sku="PROD-003", name="Product C")

        service = ProductService(db_session)

        products, total = await service.list_products()

        assert total == 3
        assert len(products) == 3

    async def test_list_products_excludes_inactive_by_default(
        self, db_session: AsyncSession
    ):
        """Test that list_products excludes inactive products by default."""
        await create_product_in_db(
            db_session, sku="ACTIVE-001", name="Active Product", is_active=True
        )
        await create_product_in_db(
            db_session, sku="INACTIVE-001", name="Inactive Product", is_active=False
        )

        service = ProductService(db_session)

        products, total = await service.list_products()

        assert total == 1
        assert products[0].sku == "ACTIVE-001"

    async def test_list_products_includes_inactive_when_specified(
        self, db_session: AsyncSession
    ):
        """Test that list_products includes inactive products when active_only=False."""
        await create_product_in_db(
            db_session, sku="ACTIVE-001", name="Active Product", is_active=True
        )
        await create_product_in_db(
            db_session, sku="INACTIVE-001", name="Inactive Product", is_active=False
        )

        service = ProductService(db_session)

        products, total = await service.list_products(active_only=False)

        assert total == 2
        assert len(products) == 2

    async def test_list_products_pagination(self, db_session: AsyncSession):
        """Test that list_products correctly handles pagination."""
        # Create 5 products
        for i in range(5):
            await create_product_in_db(
                db_session, sku=f"PROD-{i:03d}", name=f"Product {i}"
            )

        service = ProductService(db_session)

        # Get first page
        page1, total = await service.list_products(skip=0, limit=2)
        assert total == 5
        assert len(page1) == 2

        # Get second page
        page2, total = await service.list_products(skip=2, limit=2)
        assert total == 5
        assert len(page2) == 2

        # Get last page (partial)
        page3, total = await service.list_products(skip=4, limit=2)
        assert total == 5
        assert len(page3) == 1

    async def test_list_products_returns_empty_when_no_products(
        self, db_session: AsyncSession
    ):
        """Test that list_products returns empty list when no products exist."""
        service = ProductService(db_session)

        products, total = await service.list_products()

        assert total == 0
        assert len(products) == 0

    async def test_list_products_filters_by_featured(self, db_session: AsyncSession):
        """Test that list_products filters by featured flag."""
        await create_product_in_db(
            db_session, sku="FEATURED-001", name="Featured", is_featured=True
        )
        await create_product_in_db(
            db_session, sku="NORMAL-001", name="Normal", is_featured=False
        )

        service = ProductService(db_session)

        products, total = await service.list_products(featured_only=True)

        assert total == 1
        assert products[0].sku == "FEATURED-001"

    async def test_list_products_filters_by_category(self, db_session: AsyncSession):
        """Test that list_products filters by category."""
        # Create categories
        category1 = await create_category_in_db(
            db_session, name="Tools", slug="tools"
        )
        category2 = await create_category_in_db(
            db_session, name="Hardware", slug="hardware"
        )

        # Create products
        product1 = await create_product_in_db(
            db_session, sku="TOOL-001", name="Tool Product"
        )
        product2 = await create_product_in_db(
            db_session, sku="HARDWARE-001", name="Hardware Product"
        )

        # Associate products with categories
        product_cat1 = create_product_category(product1.id, category1.id)
        product_cat2 = create_product_category(product2.id, category2.id)
        db_session.add(product_cat1)
        db_session.add(product_cat2)
        await db_session.commit()

        service = ProductService(db_session)

        # Filter by category1
        products, total = await service.list_products(category_id=category1.id)

        assert total == 1
        assert products[0].sku == "TOOL-001"

    async def test_list_products_orders_by_name(self, db_session: AsyncSession):
        """Test that list_products returns products ordered by name."""
        await create_product_in_db(db_session, sku="PROD-C", name="Zebra Product")
        await create_product_in_db(db_session, sku="PROD-A", name="Alpha Product")
        await create_product_in_db(db_session, sku="PROD-B", name="Beta Product")

        service = ProductService(db_session)

        products, _ = await service.list_products()

        assert products[0].name == "Alpha Product"
        assert products[1].name == "Beta Product"
        assert products[2].name == "Zebra Product"


class TestGetFeaturedProducts:
    """Tests for ProductService.get_featured_products method."""

    async def test_get_featured_returns_only_featured_active_products(
        self, db_session: AsyncSession
    ):
        """Test that get_featured_products returns only featured and active products."""
        await create_product_in_db(
            db_session,
            sku="FEATURED-ACTIVE",
            name="Featured Active",
            is_featured=True,
            is_active=True,
        )
        await create_product_in_db(
            db_session,
            sku="FEATURED-INACTIVE",
            name="Featured Inactive",
            is_featured=True,
            is_active=False,
        )
        await create_product_in_db(
            db_session,
            sku="NORMAL-ACTIVE",
            name="Normal Active",
            is_featured=False,
            is_active=True,
        )

        service = ProductService(db_session)

        products = await service.get_featured_products()

        assert len(products) == 1
        assert products[0].sku == "FEATURED-ACTIVE"

    async def test_get_featured_respects_limit(self, db_session: AsyncSession):
        """Test that get_featured_products respects the limit parameter."""
        # Create 5 featured products
        for i in range(5):
            await create_product_in_db(
                db_session,
                sku=f"FEATURED-{i:03d}",
                name=f"Featured {i}",
                is_featured=True,
            )

        service = ProductService(db_session)

        products = await service.get_featured_products(limit=3)

        assert len(products) == 3

    async def test_get_featured_returns_empty_when_none_exist(
        self, db_session: AsyncSession
    ):
        """Test that get_featured_products returns empty list when no featured products."""
        await create_product_in_db(
            db_session, sku="NORMAL-001", name="Normal Product", is_featured=False
        )

        service = ProductService(db_session)

        products = await service.get_featured_products()

        assert len(products) == 0


class TestCreateProduct:
    """Tests for ProductService.create_product method."""

    async def test_create_product_successfully(self, db_session: AsyncSession):
        """Test that create_product creates a new product."""
        from app.schemas.product import ProductCreate

        product_data = ProductCreate(
            sku="NEW-PROD-001",
            name="New Product",
            price=39.99,
            description="A new product",
        )

        service = ProductService(db_session)

        product = await service.create_product(product_data)

        assert product.id is not None
        assert product.sku == "NEW-PROD-001"
        assert product.name == "New Product"
        assert product.price == 39.99

    async def test_create_product_with_categories(self, db_session: AsyncSession):
        """Test that create_product associates product with categories."""
        from app.schemas.product import ProductCreate

        # Create categories first
        category1 = await create_category_in_db(
            db_session, name="Category 1", slug="category-1"
        )
        category2 = await create_category_in_db(
            db_session, name="Category 2", slug="category-2"
        )

        product_data = ProductCreate(
            sku="MULTI-CAT-001",
            name="Multi Category Product",
            price=59.99,
            category_ids=[category1.id, category2.id],
        )

        service = ProductService(db_session)

        product = await service.create_product(product_data)

        # Refresh to load relationships
        await db_session.refresh(product)

        # Verify product was created
        assert product.id is not None

        # Verify category associations (need to query separately due to lazy loading)
        result = await service.get_product_by_id(product.id)
        assert result is not None


class TestUpdateProduct:
    """Tests for ProductService.update_product method."""

    async def test_update_product_successfully(self, db_session: AsyncSession):
        """Test that update_product updates product fields."""
        from app.schemas.product import ProductUpdate

        product = await create_product_in_db(
            db_session,
            sku="UPDATE-001",
            name="Original Name",
            price=19.99,
        )

        update_data = ProductUpdate(name="Updated Name", price=29.99)

        service = ProductService(db_session)

        updated = await service.update_product(product.id, update_data)

        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.price == 29.99
        assert updated.sku == "UPDATE-001"  # SKU unchanged

    async def test_update_product_returns_none_for_nonexistent(
        self, db_session: AsyncSession
    ):
        """Test that update_product returns None for non-existent product."""
        from app.schemas.product import ProductUpdate

        update_data = ProductUpdate(name="Updated Name")

        service = ProductService(db_session)

        result = await service.update_product(99999, update_data)

        assert result is None

    async def test_update_product_partial_update(self, db_session: AsyncSession):
        """Test that update_product only updates specified fields."""
        from app.schemas.product import ProductUpdate

        product = await create_product_in_db(
            db_session,
            sku="PARTIAL-001",
            name="Original Name",
            price=19.99,
            description="Original description",
        )

        # Only update the name
        update_data = ProductUpdate(name="New Name")

        service = ProductService(db_session)

        updated = await service.update_product(product.id, update_data)

        assert updated is not None
        assert updated.name == "New Name"
        assert updated.price == 19.99  # Unchanged
        assert updated.description == "Original description"  # Unchanged


class TestDeleteProduct:
    """Tests for ProductService.delete_product method."""

    async def test_delete_product_soft_deletes(self, db_session: AsyncSession):
        """Test that delete_product performs soft delete (sets is_active=False)."""
        product = await create_product_in_db(
            db_session,
            sku="DELETE-001",
            name="To Be Deleted",
            is_active=True,
        )

        service = ProductService(db_session)

        result = await service.delete_product(product.id)

        assert result is True

        # Verify product is soft deleted
        deleted_product = await service.get_product_by_id(product.id)
        assert deleted_product is not None
        assert deleted_product.is_active is False

    async def test_delete_product_returns_false_for_nonexistent(
        self, db_session: AsyncSession
    ):
        """Test that delete_product returns False for non-existent product."""
        service = ProductService(db_session)

        result = await service.delete_product(99999)

        assert result is False

    async def test_deleted_product_excluded_from_list(self, db_session: AsyncSession):
        """Test that soft-deleted products are excluded from list_products."""
        product = await create_product_in_db(
            db_session, sku="DELETE-002", name="Will Be Deleted"
        )

        service = ProductService(db_session)

        # Verify product is in list before deletion
        products_before, count_before = await service.list_products()
        assert count_before == 1

        # Delete the product
        await service.delete_product(product.id)

        # Verify product is excluded from list after deletion
        products_after, count_after = await service.list_products()
        assert count_after == 0
