"""Integration tests for category API routes.

This module contains tests for the /api/categories endpoints,
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


class TestListCategories:
    """Tests for GET /api/categories endpoint."""

    @pytest.mark.asyncio
    async def test_list_categories_returns_empty_list_when_no_categories(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that list categories returns empty list when no categories exist."""
        response = await test_client.get("/api/categories")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    @pytest.mark.asyncio
    async def test_list_categories_returns_all_active_categories(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that list categories returns all active categories."""
        # Arrange
        await create_category_in_db(
            db_session, name="Tools", slug="tools", display_order=1
        )
        await create_category_in_db(
            db_session, name="Hardware", slug="hardware", display_order=2
        )
        await create_category_in_db(
            db_session, name="Paint", slug="paint", display_order=3
        )

        # Act
        response = await test_client.get("/api/categories")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    @pytest.mark.asyncio
    async def test_list_categories_excludes_inactive(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that list categories excludes inactive categories."""
        # Arrange
        await create_category_in_db(
            db_session, name="Active Category", slug="active", is_active=True
        )
        await create_category_in_db(
            db_session, name="Inactive Category", slug="inactive", is_active=False
        )

        # Act
        response = await test_client.get("/api/categories")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["slug"] == "active"

    @pytest.mark.asyncio
    async def test_list_categories_root_only(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that list categories can filter to only root categories."""
        # Arrange - create parent category
        parent = await create_category_in_db(
            db_session, name="Parent Category", slug="parent", parent_id=None
        )
        # Create child category
        await create_category_in_db(
            db_session, name="Child Category", slug="child", parent_id=parent.id
        )

        # Act - get only root categories
        response = await test_client.get("/api/categories?root_only=true")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["slug"] == "parent"
        assert data[0]["parent_id"] is None

    @pytest.mark.asyncio
    async def test_list_categories_includes_all_when_root_only_false(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that list categories includes child categories when root_only=false."""
        # Arrange
        parent = await create_category_in_db(
            db_session, name="Parent Category", slug="parent"
        )
        await create_category_in_db(
            db_session, name="Child Category", slug="child", parent_id=parent.id
        )

        # Act
        response = await test_client.get("/api/categories?root_only=false")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


class TestGetCategoryTree:
    """Tests for GET /api/categories/tree endpoint."""

    @pytest.mark.asyncio
    async def test_get_category_tree_returns_nested_structure(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that category tree returns nested structure with children."""
        # Arrange - create parent with child
        parent = await create_category_in_db(
            db_session, name="Tools", slug="tools"
        )
        await create_category_in_db(
            db_session, name="Power Tools", slug="power-tools", parent_id=parent.id
        )

        # Act
        response = await test_client.get("/api/categories/tree")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1  # Only root category at top level
        assert data[0]["slug"] == "tools"
        assert len(data[0]["children"]) == 1
        assert data[0]["children"][0]["slug"] == "power-tools"

    @pytest.mark.asyncio
    async def test_get_category_tree_returns_empty_for_no_categories(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that category tree returns empty list when no categories exist."""
        response = await test_client.get("/api/categories/tree")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    @pytest.mark.asyncio
    async def test_get_category_tree_multiple_levels(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that category tree handles multiple levels correctly."""
        # Arrange - create 3-level hierarchy
        level1 = await create_category_in_db(
            db_session, name="Level 1", slug="level-1"
        )
        level2 = await create_category_in_db(
            db_session, name="Level 2", slug="level-2", parent_id=level1.id
        )
        await create_category_in_db(
            db_session, name="Level 3", slug="level-3", parent_id=level2.id
        )

        # Act
        response = await test_client.get("/api/categories/tree")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["slug"] == "level-1"
        assert len(data[0]["children"]) == 1
        assert data[0]["children"][0]["slug"] == "level-2"
        assert len(data[0]["children"][0]["children"]) == 1
        assert data[0]["children"][0]["children"][0]["slug"] == "level-3"

    @pytest.mark.asyncio
    async def test_get_category_tree_excludes_inactive_children(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that category tree excludes inactive child categories."""
        # Arrange
        parent = await create_category_in_db(
            db_session, name="Parent", slug="parent"
        )
        await create_category_in_db(
            db_session,
            name="Active Child",
            slug="active-child",
            parent_id=parent.id,
            is_active=True,
        )
        await create_category_in_db(
            db_session,
            name="Inactive Child",
            slug="inactive-child",
            parent_id=parent.id,
            is_active=False,
        )

        # Act
        response = await test_client.get("/api/categories/tree")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data[0]["children"]) == 1
        assert data[0]["children"][0]["slug"] == "active-child"


class TestGetCategoryBySlug:
    """Tests for GET /api/categories/{slug} endpoint."""

    @pytest.mark.asyncio
    async def test_get_category_returns_category_with_products(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that get category by slug returns category with products."""
        # Arrange - create category and product
        category = await create_category_in_db(
            db_session,
            name="Tools",
            slug="tools",
            description="All kinds of tools",
        )
        product = await create_product_in_db(
            db_session, sku="TOOL-001", name="Hammer", price=19.99
        )
        # Associate product with category
        db_session.add(create_product_category(product.id, category.id))
        await db_session.commit()

        # Act
        response = await test_client.get("/api/categories/tools")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "tools"
        assert data["name"] == "Tools"
        assert data["description"] == "All kinds of tools"
        assert data["product_count"] == 1
        assert len(data["products"]) == 1
        assert data["products"][0]["sku"] == "TOOL-001"

    @pytest.mark.asyncio
    async def test_get_category_returns_404_for_nonexistent(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that get category returns 404 for non-existent slug."""
        response = await test_client.get("/api/categories/nonexistent-slug")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_category_with_empty_products(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that get category works when category has no products."""
        # Arrange
        await create_category_in_db(
            db_session, name="Empty Category", slug="empty-category"
        )

        # Act
        response = await test_client.get("/api/categories/empty-category")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "empty-category"
        assert data["product_count"] == 0
        assert data["products"] == []

    @pytest.mark.asyncio
    async def test_get_category_paginates_products(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that get category paginates products correctly."""
        # Arrange - create category with 5 products
        category = await create_category_in_db(
            db_session, name="Many Products", slug="many-products"
        )
        for i in range(5):
            product = await create_product_in_db(
                db_session, sku=f"PROD-{i:03d}", name=f"Product {i}"
            )
            db_session.add(create_product_category(product.id, category.id))
        await db_session.commit()

        # Act - get first page with 2 items
        response = await test_client.get(
            "/api/categories/many-products?page=1&page_size=2"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["product_count"] == 5  # Total products
        assert len(data["products"]) == 2  # Only 2 on this page


class TestCreateCategory:
    """Tests for POST /api/categories endpoint."""

    @pytest.mark.asyncio
    async def test_create_category_successfully(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that creating a category returns 201 and category data."""
        # Arrange
        category_data = {
            "name": "New Category",
            "slug": "new-category",
            "description": "A new category description",
            "display_order": 5,
        }

        # Act
        response = await test_client.post("/api/categories", json=category_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Category"
        assert data["slug"] == "new-category"
        assert data["description"] == "A new category description"
        assert data["display_order"] == 5

    @pytest.mark.asyncio
    async def test_create_category_returns_409_for_duplicate_slug(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that creating a category with existing slug returns 409."""
        # Arrange
        await create_category_in_db(
            db_session, name="Existing", slug="existing-slug"
        )

        category_data = {
            "name": "Another Category",
            "slug": "existing-slug",
        }

        # Act
        response = await test_client.post("/api/categories", json=category_data)

        # Assert
        assert response.status_code == 409
        data = response.json()
        assert "already exists" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_category_with_parent(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that creating a child category works correctly."""
        # Arrange - create parent first
        parent = await create_category_in_db(
            db_session, name="Parent", slug="parent"
        )

        category_data = {
            "name": "Child Category",
            "slug": "child-category",
            "parent_id": parent.id,
        }

        # Act
        response = await test_client.post("/api/categories", json=category_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["parent_id"] == parent.id


class TestUpdateCategory:
    """Tests for PATCH /api/categories/{slug} endpoint."""

    @pytest.mark.asyncio
    async def test_update_category_successfully(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that updating a category returns updated data."""
        # Arrange
        await create_category_in_db(
            db_session, name="Original Name", slug="original-slug"
        )

        update_data = {"name": "Updated Name", "description": "Updated description"}

        # Act
        response = await test_client.patch(
            "/api/categories/original-slug", json=update_data
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated description"
        assert data["slug"] == "original-slug"  # Slug unchanged

    @pytest.mark.asyncio
    async def test_update_category_returns_404_for_nonexistent(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that updating a non-existent category returns 404."""
        update_data = {"name": "New Name"}

        response = await test_client.patch(
            "/api/categories/nonexistent-slug", json=update_data
        )

        assert response.status_code == 404


class TestDeleteCategory:
    """Tests for DELETE /api/categories/{slug} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_category_returns_204(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that deleting a category returns 204 No Content."""
        # Arrange
        await create_category_in_db(
            db_session, name="To Delete", slug="to-delete"
        )

        # Act
        response = await test_client.delete("/api/categories/to-delete")

        # Assert
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_category_returns_404_for_nonexistent(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that deleting a non-existent category returns 404."""
        response = await test_client.delete("/api/categories/nonexistent-slug")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_deleted_category_excluded_from_list(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that soft-deleted categories are excluded from list."""
        # Arrange
        await create_category_in_db(
            db_session, name="Delete Check", slug="delete-check"
        )

        # Verify category exists
        response = await test_client.get("/api/categories")
        assert response.status_code == 200
        assert len(response.json()) == 1

        # Delete the category
        await test_client.delete("/api/categories/delete-check")

        # Verify category is excluded from list
        response = await test_client.get("/api/categories")
        assert response.status_code == 200
        assert len(response.json()) == 0
