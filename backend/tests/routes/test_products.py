"""Integration tests for product API routes.

This module contains tests for the /api/products endpoints,
verifying that the routes correctly handle requests and return
appropriate responses.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import (
    create_category_in_db,
    create_product_category,
    create_product_in_db,
)


class TestListProducts:
    """Tests for GET /api/products endpoint."""

    @pytest.mark.asyncio
    async def test_list_products_returns_empty_list_when_no_products(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that list products returns empty list when no products exist."""
        response = await test_client.get("/api/products")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert data["pages"] == 1

    @pytest.mark.asyncio
    async def test_list_products_returns_all_products(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that list products returns all active products."""
        # Arrange - create test products
        await create_product_in_db(
            db_session, sku="PROD-001", name="Product A", price=19.99
        )
        await create_product_in_db(
            db_session, sku="PROD-002", name="Product B", price=29.99
        )
        await create_product_in_db(
            db_session, sku="PROD-003", name="Product C", price=39.99
        )

        # Act
        response = await test_client.get("/api/products")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3
        assert data["page"] == 1
        assert data["pages"] == 1

    @pytest.mark.asyncio
    async def test_list_products_excludes_inactive_products(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that list products excludes inactive products by default."""
        # Arrange
        await create_product_in_db(
            db_session, sku="ACTIVE-001", name="Active Product", is_active=True
        )
        await create_product_in_db(
            db_session, sku="INACTIVE-001", name="Inactive Product", is_active=False
        )

        # Act
        response = await test_client.get("/api/products")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["sku"] == "ACTIVE-001"

    @pytest.mark.asyncio
    async def test_list_products_pagination(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that list products handles pagination correctly."""
        # Arrange - create 5 products
        for i in range(5):
            await create_product_in_db(
                db_session, sku=f"PROD-{i:03d}", name=f"Product {i}", price=10.0 + i
            )

        # Act - get first page
        response = await test_client.get("/api/products?page=1&page_size=2")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert data["pages"] == 3  # ceil(5/2) = 3

    @pytest.mark.asyncio
    async def test_list_products_second_page(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test fetching second page of products."""
        # Arrange - create 5 products
        for i in range(5):
            await create_product_in_db(
                db_session, sku=f"PAGE-{i:03d}", name=f"Page Product {i}", price=10.0 + i
            )

        # Act - get second page
        response = await test_client.get("/api/products?page=2&page_size=2")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["page"] == 2

    @pytest.mark.asyncio
    async def test_list_products_filters_by_featured(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that list products can filter by featured flag."""
        # Arrange
        await create_product_in_db(
            db_session, sku="FEATURED-001", name="Featured Product", is_featured=True
        )
        await create_product_in_db(
            db_session, sku="NORMAL-001", name="Normal Product", is_featured=False
        )

        # Act
        response = await test_client.get("/api/products?featured=true")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["sku"] == "FEATURED-001"
        assert data["items"][0]["is_featured"] is True

    @pytest.mark.asyncio
    async def test_list_products_filters_by_category(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that list products can filter by category ID."""
        # Arrange - create categories
        category = await create_category_in_db(
            db_session, name="Tools", slug="tools"
        )
        other_category = await create_category_in_db(
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
        db_session.add(create_product_category(product1.id, category.id))
        db_session.add(create_product_category(product2.id, other_category.id))
        await db_session.commit()

        # Act
        response = await test_client.get(f"/api/products?category_id={category.id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["sku"] == "TOOL-001"


class TestGetFeaturedProducts:
    """Tests for GET /api/products/featured endpoint."""

    @pytest.mark.asyncio
    async def test_get_featured_returns_featured_products(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that featured endpoint returns featured products."""
        # Arrange
        await create_product_in_db(
            db_session,
            sku="FEATURED-001",
            name="Featured Product 1",
            is_featured=True,
        )
        await create_product_in_db(
            db_session,
            sku="FEATURED-002",
            name="Featured Product 2",
            is_featured=True,
        )
        await create_product_in_db(
            db_session,
            sku="NORMAL-001",
            name="Normal Product",
            is_featured=False,
        )

        # Act
        response = await test_client.get("/api/products/featured")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for product in data:
            assert product["is_featured"] is True

    @pytest.mark.asyncio
    async def test_get_featured_returns_empty_when_no_featured(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that featured endpoint returns empty list when no featured products."""
        # Arrange
        await create_product_in_db(
            db_session, sku="NORMAL-001", name="Normal Product", is_featured=False
        )

        # Act
        response = await test_client.get("/api/products/featured")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_get_featured_respects_limit(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that featured endpoint respects limit parameter."""
        # Arrange - create 5 featured products
        for i in range(5):
            await create_product_in_db(
                db_session,
                sku=f"FEATURED-{i:03d}",
                name=f"Featured {i}",
                is_featured=True,
            )

        # Act
        response = await test_client.get("/api/products/featured?limit=3")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    @pytest.mark.asyncio
    async def test_get_featured_excludes_inactive_products(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that featured endpoint excludes inactive products."""
        # Arrange
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

        # Act
        response = await test_client.get("/api/products/featured")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["sku"] == "FEATURED-ACTIVE"


class TestGetProductBySku:
    """Tests for GET /api/products/{sku} endpoint."""

    @pytest.mark.asyncio
    async def test_get_product_returns_product_details(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that get product by SKU returns full product details."""
        # Arrange
        await create_product_in_db(
            db_session,
            sku="TEST-SKU-001",
            name="Test Product",
            description="Full description here",
            price=49.99,
            is_featured=True,
            attributes={"color": "red", "size": "large"},
            specifications={"weight": "500g", "material": "steel"},
        )

        # Act
        response = await test_client.get("/api/products/TEST-SKU-001")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["sku"] == "TEST-SKU-001"
        assert data["name"] == "Test Product"
        assert data["description"] == "Full description here"
        assert data["price"] == 49.99
        assert data["is_featured"] is True
        assert data["attributes"] == {"color": "red", "size": "large"}
        assert data["specifications"] == {"weight": "500g", "material": "steel"}

    @pytest.mark.asyncio
    async def test_get_product_returns_404_for_nonexistent(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that get product returns 404 for non-existent SKU."""
        response = await test_client.get("/api/products/NONEXISTENT-SKU")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_product_includes_timestamps(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that get product returns created_at and updated_at timestamps."""
        # Arrange
        await create_product_in_db(
            db_session, sku="TIMESTAMP-001", name="Timestamp Product"
        )

        # Act
        response = await test_client.get("/api/products/TIMESTAMP-001")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "created_at" in data
        assert "updated_at" in data
        assert data["created_at"] is not None
        assert data["updated_at"] is not None


class TestCreateProduct:
    """Tests for POST /api/products endpoint."""

    @pytest.mark.asyncio
    async def test_create_product_successfully(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that creating a product returns 201 and product data."""
        # Arrange
        product_data = {
            "sku": "NEW-PRODUCT-001",
            "name": "New Product",
            "price": 29.99,
            "description": "A new product description",
        }

        # Act
        response = await test_client.post("/api/products", json=product_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["sku"] == "NEW-PRODUCT-001"
        assert data["name"] == "New Product"
        assert data["price"] == 29.99

    @pytest.mark.asyncio
    async def test_create_product_returns_409_for_duplicate_sku(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that creating a product with existing SKU returns 409."""
        # Arrange - create existing product
        await create_product_in_db(
            db_session, sku="DUPLICATE-SKU", name="Existing Product"
        )

        product_data = {
            "sku": "DUPLICATE-SKU",
            "name": "Another Product",
            "price": 19.99,
        }

        # Act
        response = await test_client.post("/api/products", json=product_data)

        # Assert
        assert response.status_code == 409
        data = response.json()
        assert "already exists" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_product_validates_required_fields(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that creating a product without required fields returns 422."""
        # Arrange - missing sku, name, and price
        product_data = {"description": "Only description provided"}

        # Act
        response = await test_client.post("/api/products", json=product_data)

        # Assert
        assert response.status_code == 422  # Validation error


class TestUpdateProduct:
    """Tests for PATCH /api/products/{sku} endpoint."""

    @pytest.mark.asyncio
    async def test_update_product_successfully(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that updating a product returns updated data."""
        # Arrange
        await create_product_in_db(
            db_session,
            sku="UPDATE-SKU-001",
            name="Original Name",
            price=19.99,
        )

        update_data = {"name": "Updated Name", "price": 29.99}

        # Act
        response = await test_client.patch("/api/products/UPDATE-SKU-001", json=update_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["price"] == 29.99
        assert data["sku"] == "UPDATE-SKU-001"  # SKU unchanged

    @pytest.mark.asyncio
    async def test_update_product_returns_404_for_nonexistent(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that updating a non-existent product returns 404."""
        update_data = {"name": "New Name"}

        response = await test_client.patch("/api/products/NONEXISTENT-SKU", json=update_data)

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_product_partial_update(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that partial update only changes specified fields."""
        # Arrange
        await create_product_in_db(
            db_session,
            sku="PARTIAL-SKU",
            name="Original Name",
            price=19.99,
            short_description="Original description",
        )

        update_data = {"name": "New Name"}  # Only update name

        # Act
        response = await test_client.patch("/api/products/PARTIAL-SKU", json=update_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["price"] == 19.99  # Unchanged
        assert data["short_description"] == "Original description"  # Unchanged


class TestDeleteProduct:
    """Tests for DELETE /api/products/{sku} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_product_returns_204(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that deleting a product returns 204 No Content."""
        # Arrange
        await create_product_in_db(
            db_session, sku="DELETE-SKU-001", name="To Be Deleted"
        )

        # Act
        response = await test_client.delete("/api/products/DELETE-SKU-001")

        # Assert
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_product_returns_404_for_nonexistent(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that deleting a non-existent product returns 404."""
        response = await test_client.delete("/api/products/NONEXISTENT-SKU")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_deleted_product_excluded_from_list(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that soft-deleted products are excluded from list."""
        # Arrange
        await create_product_in_db(
            db_session, sku="DELETE-CHECK-001", name="To Be Deleted"
        )

        # Verify product exists in list
        response = await test_client.get("/api/products")
        assert response.status_code == 200
        assert response.json()["total"] == 1

        # Delete the product
        await test_client.delete("/api/products/DELETE-CHECK-001")

        # Verify product is excluded from list
        response = await test_client.get("/api/products")
        assert response.status_code == 200
        assert response.json()["total"] == 0
