"""Tests for ListService business logic.

This module contains unit tests for the ListService, covering
shopping list management, item operations, and QR sharing functionality.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.list import ListItemCreate, ListItemUpdate, UserListCreate, UserListUpdate
from app.services.list_service import ListService
from tests.factories import (
    create_list_item_in_db,
    create_product_in_db,
    create_session_in_db,
    create_user_list_in_db,
)


class TestCreateList:
    """Tests for ListService.create_list method."""

    async def test_create_list_successfully(self, db_session: AsyncSession):
        """Test that create_list creates a new shopping list."""
        # Arrange
        user_session = await create_session_in_db(db_session)
        list_data = UserListCreate(name="My Shopping List", description="Weekend project")

        service = ListService(db_session)

        # Act
        result = await service.create_list(user_session.id, list_data)

        # Assert
        assert result is not None
        assert result.id is not None
        assert result.list_id is not None
        assert result.session_id == user_session.id
        assert result.name == "My Shopping List"
        assert result.description == "Weekend project"
        assert result.share_code is None

    async def test_create_list_with_default_name(self, db_session: AsyncSession):
        """Test that create_list uses default name when not specified."""
        user_session = await create_session_in_db(db_session)
        list_data = UserListCreate()  # Uses default name "My List"

        service = ListService(db_session)

        result = await service.create_list(user_session.id, list_data)

        assert result is not None
        assert result.name == "My List"

    async def test_create_multiple_lists_for_session(self, db_session: AsyncSession):
        """Test that multiple lists can be created for the same session."""
        user_session = await create_session_in_db(db_session)

        service = ListService(db_session)

        list1 = await service.create_list(
            user_session.id, UserListCreate(name="List 1")
        )
        list2 = await service.create_list(
            user_session.id, UserListCreate(name="List 2")
        )

        assert list1.id != list2.id
        assert list1.list_id != list2.list_id
        assert list1.session_id == list2.session_id


class TestGetListById:
    """Tests for ListService.get_list_by_id method."""

    async def test_get_list_by_id_returns_list(self, db_session: AsyncSession):
        """Test that get_list_by_id returns the correct list."""
        user_session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(
            db_session,
            session_id=user_session.id,
            name="Test List",
        )

        service = ListService(db_session)

        result = await service.get_list_by_id(user_list.list_id)

        assert result is not None
        assert result.id == user_list.id
        assert result.list_id == user_list.list_id
        assert result.name == "Test List"

    async def test_get_list_by_id_returns_none_for_nonexistent(
        self, db_session: AsyncSession
    ):
        """Test that get_list_by_id returns None for non-existent list."""
        service = ListService(db_session)

        result = await service.get_list_by_id("nonexistent-uuid")

        assert result is None

    async def test_get_list_by_id_includes_items(self, db_session: AsyncSession):
        """Test that get_list_by_id eagerly loads list items."""
        user_session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(
            db_session, session_id=user_session.id
        )
        product = await create_product_in_db(db_session, sku="TEST-001")
        await create_list_item_in_db(
            db_session,
            list_id=user_list.id,
            product_id=product.id,
            quantity=2,
        )

        service = ListService(db_session)

        result = await service.get_list_by_id(user_list.list_id)

        assert result is not None
        assert len(result.items) == 1
        assert result.items[0].quantity == 2


class TestGetListsForSession:
    """Tests for ListService.get_lists_for_session method."""

    async def test_get_lists_for_session_returns_all_lists(
        self, db_session: AsyncSession
    ):
        """Test that get_lists_for_session returns all lists for a session."""
        user_session = await create_session_in_db(db_session)
        await create_user_list_in_db(
            db_session, session_id=user_session.id, name="List A"
        )
        await create_user_list_in_db(
            db_session, session_id=user_session.id, name="List B"
        )
        await create_user_list_in_db(
            db_session, session_id=user_session.id, name="List C"
        )

        service = ListService(db_session)

        result = await service.get_lists_for_session(user_session.id)

        assert len(result) == 3

    async def test_get_lists_for_session_returns_empty_for_no_lists(
        self, db_session: AsyncSession
    ):
        """Test that get_lists_for_session returns empty list when no lists exist."""
        user_session = await create_session_in_db(db_session)

        service = ListService(db_session)

        result = await service.get_lists_for_session(user_session.id)

        assert len(result) == 0

    async def test_get_lists_for_session_only_returns_own_lists(
        self, db_session: AsyncSession
    ):
        """Test that get_lists_for_session only returns lists for the given session."""
        session1 = await create_session_in_db(db_session)
        session2 = await create_session_in_db(db_session)

        await create_user_list_in_db(
            db_session, session_id=session1.id, name="Session 1 List"
        )
        await create_user_list_in_db(
            db_session, session_id=session2.id, name="Session 2 List"
        )

        service = ListService(db_session)

        result = await service.get_lists_for_session(session1.id)

        assert len(result) == 1
        assert result[0].name == "Session 1 List"


class TestUpdateList:
    """Tests for ListService.update_list method."""

    async def test_update_list_successfully(self, db_session: AsyncSession):
        """Test that update_list updates list fields."""
        user_session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(
            db_session,
            session_id=user_session.id,
            name="Original Name",
            description="Original description",
        )

        update_data = UserListUpdate(name="Updated Name", description="New description")

        service = ListService(db_session)

        result = await service.update_list(user_list.list_id, update_data)

        assert result is not None
        assert result.name == "Updated Name"
        assert result.description == "New description"

    async def test_update_list_partial_update(self, db_session: AsyncSession):
        """Test that update_list only updates specified fields."""
        user_session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(
            db_session,
            session_id=user_session.id,
            name="Original Name",
            description="Original description",
        )

        update_data = UserListUpdate(name="New Name")

        service = ListService(db_session)

        result = await service.update_list(user_list.list_id, update_data)

        assert result is not None
        assert result.name == "New Name"
        assert result.description == "Original description"

    async def test_update_list_returns_none_for_nonexistent(
        self, db_session: AsyncSession
    ):
        """Test that update_list returns None for non-existent list."""
        update_data = UserListUpdate(name="New Name")

        service = ListService(db_session)

        result = await service.update_list("nonexistent-uuid", update_data)

        assert result is None


class TestDeleteList:
    """Tests for ListService.delete_list method."""

    async def test_delete_list_successfully(self, db_session: AsyncSession):
        """Test that delete_list removes the list."""
        user_session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(
            db_session, session_id=user_session.id
        )

        service = ListService(db_session)

        result = await service.delete_list(user_list.list_id)

        assert result is True

        # Verify list is deleted
        deleted = await service.get_list_by_id(user_list.list_id)
        assert deleted is None

    async def test_delete_list_returns_false_for_nonexistent(
        self, db_session: AsyncSession
    ):
        """Test that delete_list returns False for non-existent list."""
        service = ListService(db_session)

        result = await service.delete_list("nonexistent-uuid")

        assert result is False


class TestAddItem:
    """Tests for ListService.add_item method."""

    async def test_add_item_successfully(self, db_session: AsyncSession):
        """Test that add_item adds an item to the list."""
        user_session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(
            db_session, session_id=user_session.id
        )
        product = await create_product_in_db(
            db_session, sku="ITEM-001", name="Test Product", price=19.99
        )

        item_data = ListItemCreate(product_sku="ITEM-001", quantity=2, notes="Test note")

        service = ListService(db_session)

        result = await service.add_item(user_list.list_id, item_data)

        assert result is not None
        assert result.quantity == 2
        assert result.notes == "Test note"
        assert result.price_at_add == 19.99
        assert result.product.sku == "ITEM-001"

    async def test_add_item_updates_quantity_for_existing(
        self, db_session: AsyncSession
    ):
        """Test that add_item updates quantity when item already exists."""
        user_session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(
            db_session, session_id=user_session.id
        )
        product = await create_product_in_db(db_session, sku="ITEM-002")
        await create_list_item_in_db(
            db_session,
            list_id=user_list.id,
            product_id=product.id,
            quantity=3,
        )

        item_data = ListItemCreate(product_sku="ITEM-002", quantity=2)

        service = ListService(db_session)

        result = await service.add_item(user_list.list_id, item_data)

        assert result is not None
        assert result.quantity == 5  # 3 + 2

    async def test_add_item_returns_none_for_nonexistent_list(
        self, db_session: AsyncSession
    ):
        """Test that add_item returns None for non-existent list."""
        await create_product_in_db(db_session, sku="ITEM-003")
        item_data = ListItemCreate(product_sku="ITEM-003", quantity=1)

        service = ListService(db_session)

        result = await service.add_item("nonexistent-uuid", item_data)

        assert result is None

    async def test_add_item_returns_none_for_nonexistent_product(
        self, db_session: AsyncSession
    ):
        """Test that add_item returns None for non-existent product SKU."""
        user_session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(
            db_session, session_id=user_session.id
        )
        item_data = ListItemCreate(product_sku="NONEXISTENT-SKU", quantity=1)

        service = ListService(db_session)

        result = await service.add_item(user_list.list_id, item_data)

        assert result is None

    async def test_add_item_records_price_at_add(self, db_session: AsyncSession):
        """Test that add_item records the product price at time of adding."""
        user_session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(
            db_session, session_id=user_session.id
        )
        product = await create_product_in_db(
            db_session, sku="PRICE-001", price=99.99
        )

        item_data = ListItemCreate(product_sku="PRICE-001", quantity=1)

        service = ListService(db_session)

        result = await service.add_item(user_list.list_id, item_data)

        assert result is not None
        assert result.price_at_add == 99.99


class TestUpdateItem:
    """Tests for ListService.update_item method."""

    async def test_update_item_quantity(self, db_session: AsyncSession):
        """Test that update_item updates the item quantity."""
        user_session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(
            db_session, session_id=user_session.id
        )
        product = await create_product_in_db(db_session, sku="UPDATE-001")
        await create_list_item_in_db(
            db_session,
            list_id=user_list.id,
            product_id=product.id,
            quantity=2,
        )

        update_data = ListItemUpdate(quantity=5)

        service = ListService(db_session)

        result = await service.update_item(user_list.list_id, "UPDATE-001", update_data)

        assert result is not None
        assert result.quantity == 5

    async def test_update_item_notes(self, db_session: AsyncSession):
        """Test that update_item updates the item notes."""
        user_session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(
            db_session, session_id=user_session.id
        )
        product = await create_product_in_db(db_session, sku="NOTES-001")
        await create_list_item_in_db(
            db_session,
            list_id=user_list.id,
            product_id=product.id,
            notes=None,
        )

        update_data = ListItemUpdate(notes="Updated notes")

        service = ListService(db_session)

        result = await service.update_item(user_list.list_id, "NOTES-001", update_data)

        assert result is not None
        assert result.notes == "Updated notes"

    async def test_update_item_returns_none_for_nonexistent_list(
        self, db_session: AsyncSession
    ):
        """Test that update_item returns None for non-existent list."""
        await create_product_in_db(db_session, sku="UPDATE-002")
        update_data = ListItemUpdate(quantity=10)

        service = ListService(db_session)

        result = await service.update_item("nonexistent-uuid", "UPDATE-002", update_data)

        assert result is None

    async def test_update_item_returns_none_for_nonexistent_product(
        self, db_session: AsyncSession
    ):
        """Test that update_item returns None for non-existent product SKU."""
        user_session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(
            db_session, session_id=user_session.id
        )
        update_data = ListItemUpdate(quantity=10)

        service = ListService(db_session)

        result = await service.update_item(
            user_list.list_id, "NONEXISTENT-SKU", update_data
        )

        assert result is None

    async def test_update_item_returns_none_for_item_not_in_list(
        self, db_session: AsyncSession
    ):
        """Test that update_item returns None when item is not in the list."""
        user_session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(
            db_session, session_id=user_session.id
        )
        product = await create_product_in_db(db_session, sku="NOT-IN-LIST")
        # Product exists but is not in the list
        update_data = ListItemUpdate(quantity=10)

        service = ListService(db_session)

        result = await service.update_item(user_list.list_id, "NOT-IN-LIST", update_data)

        assert result is None


class TestRemoveItem:
    """Tests for ListService.remove_item method."""

    async def test_remove_item_successfully(self, db_session: AsyncSession):
        """Test that remove_item removes the item from the list."""
        user_session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(
            db_session, session_id=user_session.id
        )
        product = await create_product_in_db(db_session, sku="REMOVE-001")
        await create_list_item_in_db(
            db_session, list_id=user_list.id, product_id=product.id
        )

        service = ListService(db_session)

        result = await service.remove_item(user_list.list_id, "REMOVE-001")

        assert result is True

        # Verify item is removed by trying to remove again (should return False)
        result_again = await service.remove_item(user_list.list_id, "REMOVE-001")
        assert result_again is False

    async def test_remove_item_returns_false_for_nonexistent_list(
        self, db_session: AsyncSession
    ):
        """Test that remove_item returns False for non-existent list."""
        service = ListService(db_session)

        result = await service.remove_item("nonexistent-uuid", "SOME-SKU")

        assert result is False

    async def test_remove_item_returns_false_for_nonexistent_product(
        self, db_session: AsyncSession
    ):
        """Test that remove_item returns False for non-existent product."""
        user_session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(
            db_session, session_id=user_session.id
        )

        service = ListService(db_session)

        result = await service.remove_item(user_list.list_id, "NONEXISTENT-SKU")

        assert result is False

    async def test_remove_item_returns_false_for_item_not_in_list(
        self, db_session: AsyncSession
    ):
        """Test that remove_item returns False when item is not in the list."""
        user_session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(
            db_session, session_id=user_session.id
        )
        product = await create_product_in_db(db_session, sku="NOT-IN-LIST-2")
        # Product exists but is not in the list

        service = ListService(db_session)

        result = await service.remove_item(user_list.list_id, "NOT-IN-LIST-2")

        assert result is False


class TestGenerateShareCode:
    """Tests for ListService.generate_share_code method."""

    async def test_generate_share_code_creates_code(self, db_session: AsyncSession):
        """Test that generate_share_code creates a share code."""
        user_session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(
            db_session, session_id=user_session.id
        )

        service = ListService(db_session)

        result = await service.generate_share_code(user_list.list_id)

        assert result is not None
        assert len(result) == 8
        assert result.isupper()

    async def test_generate_share_code_returns_existing(self, db_session: AsyncSession):
        """Test that generate_share_code returns existing code if already set."""
        user_session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(
            db_session, session_id=user_session.id, share_code="EXISTING"
        )

        service = ListService(db_session)

        result = await service.generate_share_code(user_list.list_id)

        assert result == "EXISTING"

    async def test_generate_share_code_returns_none_for_nonexistent(
        self, db_session: AsyncSession
    ):
        """Test that generate_share_code returns None for non-existent list."""
        service = ListService(db_session)

        result = await service.generate_share_code("nonexistent-uuid")

        assert result is None


class TestGetListByShareCode:
    """Tests for ListService.get_list_by_share_code method."""

    async def test_get_list_by_share_code_returns_list(self, db_session: AsyncSession):
        """Test that get_list_by_share_code returns the correct list."""
        user_session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(
            db_session,
            session_id=user_session.id,
            name="Shared List",
            share_code="TESTCODE",
        )

        service = ListService(db_session)

        result = await service.get_list_by_share_code("TESTCODE")

        assert result is not None
        assert result.id == user_list.id
        assert result.name == "Shared List"

    async def test_get_list_by_share_code_returns_none_for_nonexistent(
        self, db_session: AsyncSession
    ):
        """Test that get_list_by_share_code returns None for invalid code."""
        service = ListService(db_session)

        result = await service.get_list_by_share_code("INVALID")

        assert result is None


class TestCloneListToSession:
    """Tests for ListService.clone_list_to_session method."""

    async def test_clone_list_to_session_creates_copy(self, db_session: AsyncSession):
        """Test that clone_list_to_session creates a copy of the list."""
        # Create source session and list
        source_session = await create_session_in_db(db_session)
        source_list = await create_user_list_in_db(
            db_session,
            session_id=source_session.id,
            name="Source List",
            description="Source description",
            share_code="CLONE001",
        )

        # Create target session
        target_session = await create_session_in_db(db_session)

        service = ListService(db_session)

        result = await service.clone_list_to_session("CLONE001", target_session.id)

        assert result is not None
        assert result.id != source_list.id
        assert result.list_id != source_list.list_id
        assert result.session_id == target_session.id
        assert result.name == "Source List"
        assert result.description == "Source description"
        # Cloned list should not have the share code
        assert result.share_code is None

    async def test_clone_list_to_session_copies_items(self, db_session: AsyncSession):
        """Test that clone_list_to_session copies all items."""
        source_session = await create_session_in_db(db_session)
        source_list = await create_user_list_in_db(
            db_session,
            session_id=source_session.id,
            share_code="CLONE002",
        )
        product1 = await create_product_in_db(db_session, sku="CLONE-PROD-1")
        product2 = await create_product_in_db(db_session, sku="CLONE-PROD-2")
        await create_list_item_in_db(
            db_session,
            list_id=source_list.id,
            product_id=product1.id,
            quantity=3,
            notes="Note 1",
            price_at_add=10.00,
        )
        await create_list_item_in_db(
            db_session,
            list_id=source_list.id,
            product_id=product2.id,
            quantity=5,
            notes="Note 2",
            price_at_add=20.00,
        )

        target_session = await create_session_in_db(db_session)

        service = ListService(db_session)

        result = await service.clone_list_to_session("CLONE002", target_session.id)

        assert result is not None

        # Fetch the cloned list with items
        cloned_list = await service.get_list_by_id(result.list_id)
        assert len(cloned_list.items) == 2

        # Verify items were copied correctly
        items_by_product = {item.product_id: item for item in cloned_list.items}
        assert items_by_product[product1.id].quantity == 3
        assert items_by_product[product1.id].notes == "Note 1"
        assert items_by_product[product1.id].price_at_add == 10.00
        assert items_by_product[product2.id].quantity == 5
        assert items_by_product[product2.id].notes == "Note 2"
        assert items_by_product[product2.id].price_at_add == 20.00

    async def test_clone_list_to_session_returns_none_for_invalid_code(
        self, db_session: AsyncSession
    ):
        """Test that clone_list_to_session returns None for invalid share code."""
        target_session = await create_session_in_db(db_session)

        service = ListService(db_session)

        result = await service.clone_list_to_session("INVALID", target_session.id)

        assert result is None

    async def test_clone_list_preserves_source(self, db_session: AsyncSession):
        """Test that clone_list_to_session does not modify the source list."""
        source_session = await create_session_in_db(db_session)
        source_list = await create_user_list_in_db(
            db_session,
            session_id=source_session.id,
            name="Original",
            share_code="CLONE003",
        )
        product = await create_product_in_db(db_session, sku="CLONE-PROD-3")
        await create_list_item_in_db(
            db_session,
            list_id=source_list.id,
            product_id=product.id,
            quantity=2,
        )

        target_session = await create_session_in_db(db_session)

        service = ListService(db_session)

        # Clone the list
        await service.clone_list_to_session("CLONE003", target_session.id)

        # Verify source is unchanged
        source = await service.get_list_by_id(source_list.list_id)
        assert source.name == "Original"
        assert source.session_id == source_session.id
        assert len(source.items) == 1
        assert source.items[0].quantity == 2
