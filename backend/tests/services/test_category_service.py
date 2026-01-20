"""Tests for CategoryService business logic.

This module contains unit tests for the CategoryService, covering
category retrieval, listing, tree structure, and CRUD operations.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.category_service import CategoryService
from tests.factories import (
    create_category_in_db,
    create_product_category,
    create_product_in_db,
)


class TestGetCategoryBySlug:
    """Tests for CategoryService.get_category_by_slug method."""

    async def test_get_category_by_slug_returns_category(self, db_session: AsyncSession):
        """Test that get_category_by_slug returns the correct category."""
        # Arrange
        category = await create_category_in_db(
            db_session,
            name="Power Tools",
            slug="power-tools",
            description="All power tools",
        )

        service = CategoryService(db_session)

        # Act
        result = await service.get_category_by_slug("power-tools")

        # Assert
        assert result is not None
        assert result.slug == "power-tools"
        assert result.name == "Power Tools"
        assert result.description == "All power tools"

    async def test_get_category_by_slug_returns_none_for_nonexistent(
        self, db_session: AsyncSession
    ):
        """Test that get_category_by_slug returns None for non-existent slug."""
        service = CategoryService(db_session)

        result = await service.get_category_by_slug("nonexistent-slug")

        assert result is None

    async def test_get_category_by_slug_is_case_sensitive(self, db_session: AsyncSession):
        """Test that slug lookup is case-sensitive."""
        await create_category_in_db(
            db_session,
            name="Power Tools",
            slug="power-tools",
        )

        service = CategoryService(db_session)

        # Act - try uppercase version
        result = await service.get_category_by_slug("POWER-TOOLS")

        # Assert - should not find it (case sensitive)
        assert result is None

    async def test_get_category_by_slug_loads_children(self, db_session: AsyncSession):
        """Test that get_category_by_slug eagerly loads children."""
        parent = await create_category_in_db(
            db_session,
            name="Tools",
            slug="tools",
        )

        await create_category_in_db(
            db_session,
            name="Hand Tools",
            slug="hand-tools",
            parent_id=parent.id,
        )
        await create_category_in_db(
            db_session,
            name="Power Tools",
            slug="power-tools",
            parent_id=parent.id,
        )

        service = CategoryService(db_session)

        result = await service.get_category_by_slug("tools")

        assert result is not None
        assert len(result.children) == 2
        child_slugs = [c.slug for c in result.children]
        assert "hand-tools" in child_slugs
        assert "power-tools" in child_slugs


class TestGetCategoryById:
    """Tests for CategoryService.get_category_by_id method."""

    async def test_get_category_by_id_returns_category(self, db_session: AsyncSession):
        """Test that get_category_by_id returns the correct category."""
        category = await create_category_in_db(
            db_session,
            name="Hardware",
            slug="hardware",
            display_order=5,
        )

        service = CategoryService(db_session)

        result = await service.get_category_by_id(category.id)

        assert result is not None
        assert result.id == category.id
        assert result.name == "Hardware"
        assert result.display_order == 5

    async def test_get_category_by_id_returns_none_for_nonexistent(
        self, db_session: AsyncSession
    ):
        """Test that get_category_by_id returns None for non-existent ID."""
        service = CategoryService(db_session)

        result = await service.get_category_by_id(99999)

        assert result is None

    async def test_get_category_by_id_loads_children(self, db_session: AsyncSession):
        """Test that get_category_by_id eagerly loads children."""
        parent = await create_category_in_db(
            db_session,
            name="Fasteners",
            slug="fasteners",
        )

        await create_category_in_db(
            db_session,
            name="Bolts",
            slug="bolts",
            parent_id=parent.id,
        )

        service = CategoryService(db_session)

        result = await service.get_category_by_id(parent.id)

        assert result is not None
        assert len(result.children) == 1
        assert result.children[0].slug == "bolts"


class TestListCategories:
    """Tests for CategoryService.list_categories method."""

    async def test_list_categories_returns_all_active_categories(
        self, db_session: AsyncSession
    ):
        """Test that list_categories returns all active categories by default."""
        await create_category_in_db(db_session, name="Category A", slug="cat-a")
        await create_category_in_db(db_session, name="Category B", slug="cat-b")
        await create_category_in_db(db_session, name="Category C", slug="cat-c")

        service = CategoryService(db_session)

        categories = await service.list_categories()

        assert len(categories) == 3

    async def test_list_categories_excludes_inactive_by_default(
        self, db_session: AsyncSession
    ):
        """Test that list_categories excludes inactive categories by default."""
        await create_category_in_db(
            db_session, name="Active", slug="active-cat", is_active=True
        )
        await create_category_in_db(
            db_session, name="Inactive", slug="inactive-cat", is_active=False
        )

        service = CategoryService(db_session)

        categories = await service.list_categories()

        assert len(categories) == 1
        assert categories[0].slug == "active-cat"

    async def test_list_categories_includes_inactive_when_specified(
        self, db_session: AsyncSession
    ):
        """Test that list_categories includes inactive when active_only=False."""
        await create_category_in_db(
            db_session, name="Active", slug="active-cat", is_active=True
        )
        await create_category_in_db(
            db_session, name="Inactive", slug="inactive-cat", is_active=False
        )

        service = CategoryService(db_session)

        categories = await service.list_categories(active_only=False)

        assert len(categories) == 2

    async def test_list_categories_root_only_excludes_children(
        self, db_session: AsyncSession
    ):
        """Test that list_categories with root_only=True excludes child categories."""
        parent = await create_category_in_db(
            db_session, name="Parent", slug="parent-cat"
        )
        await create_category_in_db(
            db_session, name="Child", slug="child-cat", parent_id=parent.id
        )

        service = CategoryService(db_session)

        categories = await service.list_categories(root_only=True)

        assert len(categories) == 1
        assert categories[0].slug == "parent-cat"

    async def test_list_categories_returns_empty_when_no_categories(
        self, db_session: AsyncSession
    ):
        """Test that list_categories returns empty list when no categories exist."""
        service = CategoryService(db_session)

        categories = await service.list_categories()

        assert len(categories) == 0

    async def test_list_categories_orders_by_display_order_and_name(
        self, db_session: AsyncSession
    ):
        """Test that list_categories returns categories ordered by display_order, then name."""
        await create_category_in_db(
            db_session, name="Zebra", slug="zebra", display_order=1
        )
        await create_category_in_db(
            db_session, name="Alpha", slug="alpha", display_order=1
        )
        await create_category_in_db(
            db_session, name="Beta", slug="beta", display_order=0
        )

        service = CategoryService(db_session)

        categories = await service.list_categories()

        # Beta should be first (display_order=0), then Alpha (display_order=1, name < Zebra)
        assert categories[0].slug == "beta"
        assert categories[1].slug == "alpha"
        assert categories[2].slug == "zebra"


class TestGetCategoryTree:
    """Tests for CategoryService.get_category_tree method."""

    async def test_get_category_tree_returns_root_categories_only(
        self, db_session: AsyncSession
    ):
        """Test that get_category_tree returns only root categories."""
        root1 = await create_category_in_db(
            db_session, name="Root 1", slug="root-1"
        )
        root2 = await create_category_in_db(
            db_session, name="Root 2", slug="root-2"
        )
        await create_category_in_db(
            db_session, name="Child 1", slug="child-1", parent_id=root1.id
        )

        service = CategoryService(db_session)

        tree = await service.get_category_tree()

        assert len(tree) == 2
        root_slugs = [c.slug for c in tree]
        assert "root-1" in root_slugs
        assert "root-2" in root_slugs
        assert "child-1" not in root_slugs

    async def test_get_category_tree_has_children_loaded(self, db_session: AsyncSession):
        """Test that get_category_tree returns categories with children loaded."""
        root = await create_category_in_db(
            db_session, name="Root", slug="root"
        )
        await create_category_in_db(
            db_session, name="Child A", slug="child-a", parent_id=root.id
        )
        await create_category_in_db(
            db_session, name="Child B", slug="child-b", parent_id=root.id
        )

        service = CategoryService(db_session)

        tree = await service.get_category_tree()

        assert len(tree) == 1
        root_category = tree[0]
        assert len(root_category.children) == 2
        child_slugs = [c.slug for c in root_category.children]
        assert "child-a" in child_slugs
        assert "child-b" in child_slugs

    async def test_get_category_tree_excludes_inactive(self, db_session: AsyncSession):
        """Test that get_category_tree excludes inactive categories."""
        await create_category_in_db(
            db_session, name="Active Root", slug="active-root", is_active=True
        )
        await create_category_in_db(
            db_session, name="Inactive Root", slug="inactive-root", is_active=False
        )

        service = CategoryService(db_session)

        tree = await service.get_category_tree()

        assert len(tree) == 1
        assert tree[0].slug == "active-root"

    async def test_get_category_tree_returns_empty_when_no_categories(
        self, db_session: AsyncSession
    ):
        """Test that get_category_tree returns empty list when no categories exist."""
        service = CategoryService(db_session)

        tree = await service.get_category_tree()

        assert len(tree) == 0


class TestGetCategoryWithProducts:
    """Tests for CategoryService.get_category_with_products method."""

    async def test_get_category_with_products_returns_category_and_products(
        self, db_session: AsyncSession
    ):
        """Test that get_category_with_products returns category and its products."""
        category = await create_category_in_db(
            db_session, name="Tools", slug="tools"
        )
        product1 = await create_product_in_db(
            db_session, sku="TOOL-001", name="Hammer"
        )
        product2 = await create_product_in_db(
            db_session, sku="TOOL-002", name="Screwdriver"
        )

        # Associate products with category
        pc1 = create_product_category(product1.id, category.id)
        pc2 = create_product_category(product2.id, category.id)
        db_session.add(pc1)
        db_session.add(pc2)
        await db_session.commit()

        service = CategoryService(db_session)

        result_category, products, total = await service.get_category_with_products(
            category.id
        )

        assert result_category is not None
        assert result_category.slug == "tools"
        assert len(products) == 2
        assert total == 2
        product_skus = [p.sku for p in products]
        assert "TOOL-001" in product_skus
        assert "TOOL-002" in product_skus

    async def test_get_category_with_products_returns_none_for_nonexistent(
        self, db_session: AsyncSession
    ):
        """Test that get_category_with_products returns None for non-existent category."""
        service = CategoryService(db_session)

        result_category, products, total = await service.get_category_with_products(
            99999
        )

        assert result_category is None
        assert products == []
        assert total == 0

    async def test_get_category_with_products_excludes_inactive_products(
        self, db_session: AsyncSession
    ):
        """Test that get_category_with_products excludes inactive products."""
        category = await create_category_in_db(
            db_session, name="Tools", slug="tools"
        )
        active_product = await create_product_in_db(
            db_session, sku="ACTIVE-001", name="Active Tool", is_active=True
        )
        inactive_product = await create_product_in_db(
            db_session, sku="INACTIVE-001", name="Inactive Tool", is_active=False
        )

        # Associate products with category
        pc1 = create_product_category(active_product.id, category.id)
        pc2 = create_product_category(inactive_product.id, category.id)
        db_session.add(pc1)
        db_session.add(pc2)
        await db_session.commit()

        service = CategoryService(db_session)

        result_category, products, total = await service.get_category_with_products(
            category.id
        )

        assert result_category is not None
        assert len(products) == 1
        assert total == 1
        assert products[0].sku == "ACTIVE-001"

    async def test_get_category_with_products_pagination(self, db_session: AsyncSession):
        """Test that get_category_with_products correctly handles pagination."""
        category = await create_category_in_db(
            db_session, name="Large Category", slug="large-category"
        )

        # Create 5 products
        for i in range(5):
            product = await create_product_in_db(
                db_session, sku=f"PROD-{i:03d}", name=f"Product {i:03d}"
            )
            pc = create_product_category(product.id, category.id)
            db_session.add(pc)
        await db_session.commit()

        service = CategoryService(db_session)

        # Get first page
        _, page1, total = await service.get_category_with_products(
            category.id, skip=0, limit=2
        )
        assert total == 5
        assert len(page1) == 2

        # Get second page
        _, page2, total = await service.get_category_with_products(
            category.id, skip=2, limit=2
        )
        assert total == 5
        assert len(page2) == 2

        # Get last page (partial)
        _, page3, total = await service.get_category_with_products(
            category.id, skip=4, limit=2
        )
        assert total == 5
        assert len(page3) == 1

    async def test_get_category_with_products_empty_category(
        self, db_session: AsyncSession
    ):
        """Test that get_category_with_products handles category with no products."""
        category = await create_category_in_db(
            db_session, name="Empty Category", slug="empty-category"
        )

        service = CategoryService(db_session)

        result_category, products, total = await service.get_category_with_products(
            category.id
        )

        assert result_category is not None
        assert result_category.slug == "empty-category"
        assert products == []
        assert total == 0

    async def test_get_category_with_products_orders_by_name(
        self, db_session: AsyncSession
    ):
        """Test that get_category_with_products returns products ordered by name."""
        category = await create_category_in_db(
            db_session, name="Ordered Category", slug="ordered-category"
        )

        # Create products with different names
        product_z = await create_product_in_db(
            db_session, sku="PROD-Z", name="Zebra Tool"
        )
        product_a = await create_product_in_db(
            db_session, sku="PROD-A", name="Alpha Tool"
        )
        product_m = await create_product_in_db(
            db_session, sku="PROD-M", name="Middle Tool"
        )

        for product in [product_z, product_a, product_m]:
            pc = create_product_category(product.id, category.id)
            db_session.add(pc)
        await db_session.commit()

        service = CategoryService(db_session)

        _, products, _ = await service.get_category_with_products(category.id)

        assert products[0].name == "Alpha Tool"
        assert products[1].name == "Middle Tool"
        assert products[2].name == "Zebra Tool"


class TestCreateCategory:
    """Tests for CategoryService.create_category method."""

    async def test_create_category_successfully(self, db_session: AsyncSession):
        """Test that create_category creates a new category."""
        from app.schemas.category import CategoryCreate

        category_data = CategoryCreate(
            name="New Category",
            slug="new-category",
            description="A brand new category",
            display_order=10,
        )

        service = CategoryService(db_session)

        category = await service.create_category(category_data)

        assert category.id is not None
        assert category.slug == "new-category"
        assert category.name == "New Category"
        assert category.description == "A brand new category"
        assert category.display_order == 10

    async def test_create_category_with_parent(self, db_session: AsyncSession):
        """Test that create_category creates a child category."""
        from app.schemas.category import CategoryCreate

        parent = await create_category_in_db(
            db_session, name="Parent", slug="parent"
        )

        category_data = CategoryCreate(
            name="Child",
            slug="child",
            parent_id=parent.id,
        )

        service = CategoryService(db_session)

        child = await service.create_category(category_data)

        assert child.id is not None
        assert child.parent_id == parent.id


class TestUpdateCategory:
    """Tests for CategoryService.update_category method."""

    async def test_update_category_successfully(self, db_session: AsyncSession):
        """Test that update_category updates category fields."""
        from app.schemas.category import CategoryUpdate

        category = await create_category_in_db(
            db_session,
            name="Original Name",
            slug="original-slug",
            description="Original description",
        )

        update_data = CategoryUpdate(
            name="Updated Name", description="Updated description"
        )

        service = CategoryService(db_session)

        updated = await service.update_category(category.id, update_data)

        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.description == "Updated description"
        assert updated.slug == "original-slug"  # Unchanged

    async def test_update_category_returns_none_for_nonexistent(
        self, db_session: AsyncSession
    ):
        """Test that update_category returns None for non-existent category."""
        from app.schemas.category import CategoryUpdate

        update_data = CategoryUpdate(name="Updated Name")

        service = CategoryService(db_session)

        result = await service.update_category(99999, update_data)

        assert result is None

    async def test_update_category_partial_update(self, db_session: AsyncSession):
        """Test that update_category only updates specified fields."""
        from app.schemas.category import CategoryUpdate

        category = await create_category_in_db(
            db_session,
            name="Original Name",
            slug="original-slug",
            description="Original description",
            display_order=5,
        )

        # Only update the name
        update_data = CategoryUpdate(name="New Name")

        service = CategoryService(db_session)

        updated = await service.update_category(category.id, update_data)

        assert updated is not None
        assert updated.name == "New Name"
        assert updated.description == "Original description"  # Unchanged
        assert updated.display_order == 5  # Unchanged


class TestDeleteCategory:
    """Tests for CategoryService.delete_category method."""

    async def test_delete_category_soft_deletes(self, db_session: AsyncSession):
        """Test that delete_category performs soft delete (sets is_active=False)."""
        category = await create_category_in_db(
            db_session,
            name="To Be Deleted",
            slug="to-be-deleted",
            is_active=True,
        )

        service = CategoryService(db_session)

        result = await service.delete_category(category.id)

        assert result is True

        # Verify category is soft deleted
        deleted_category = await service.get_category_by_id(category.id)
        assert deleted_category is not None
        assert deleted_category.is_active is False

    async def test_delete_category_returns_false_for_nonexistent(
        self, db_session: AsyncSession
    ):
        """Test that delete_category returns False for non-existent category."""
        service = CategoryService(db_session)

        result = await service.delete_category(99999)

        assert result is False

    async def test_deleted_category_excluded_from_list(self, db_session: AsyncSession):
        """Test that soft-deleted categories are excluded from list_categories."""
        category = await create_category_in_db(
            db_session, name="Will Be Deleted", slug="will-be-deleted"
        )

        service = CategoryService(db_session)

        # Verify category is in list before deletion
        categories_before = await service.list_categories()
        assert len(categories_before) == 1

        # Delete the category
        await service.delete_category(category.id)

        # Verify category is excluded from list after deletion
        categories_after = await service.list_categories()
        assert len(categories_after) == 0


class TestGetProductCount:
    """Tests for CategoryService.get_product_count method."""

    async def test_get_product_count_returns_correct_count(
        self, db_session: AsyncSession
    ):
        """Test that get_product_count returns the correct number of products."""
        category = await create_category_in_db(
            db_session, name="Counted Category", slug="counted-category"
        )

        # Create 3 products and associate them with the category
        for i in range(3):
            product = await create_product_in_db(
                db_session, sku=f"COUNT-{i:03d}", name=f"Product {i}"
            )
            pc = create_product_category(product.id, category.id)
            db_session.add(pc)
        await db_session.commit()

        service = CategoryService(db_session)

        count = await service.get_product_count(category.id)

        assert count == 3

    async def test_get_product_count_returns_zero_for_empty_category(
        self, db_session: AsyncSession
    ):
        """Test that get_product_count returns 0 for category with no products."""
        category = await create_category_in_db(
            db_session, name="Empty Category", slug="empty-category"
        )

        service = CategoryService(db_session)

        count = await service.get_product_count(category.id)

        assert count == 0

    async def test_get_product_count_returns_zero_for_nonexistent_category(
        self, db_session: AsyncSession
    ):
        """Test that get_product_count returns 0 for non-existent category."""
        service = CategoryService(db_session)

        count = await service.get_product_count(99999)

        assert count == 0

    async def test_get_product_count_includes_inactive_products(
        self, db_session: AsyncSession
    ):
        """Test that get_product_count includes inactive products (counts associations)."""
        category = await create_category_in_db(
            db_session, name="Mixed Category", slug="mixed-category"
        )

        active_product = await create_product_in_db(
            db_session, sku="ACTIVE-001", name="Active Product", is_active=True
        )
        inactive_product = await create_product_in_db(
            db_session, sku="INACTIVE-001", name="Inactive Product", is_active=False
        )

        pc1 = create_product_category(active_product.id, category.id)
        pc2 = create_product_category(inactive_product.id, category.id)
        db_session.add(pc1)
        db_session.add(pc2)
        await db_session.commit()

        service = CategoryService(db_session)

        # get_product_count counts all associations, not just active products
        count = await service.get_product_count(category.id)

        assert count == 2
