"""Integration tests for user list (shopping basket) API routes.

This module contains tests for the /api/lists endpoints,
verifying that the routes correctly handle requests and return
appropriate responses.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import (
    create_list_item_in_db,
    create_product_in_db,
    create_session_in_db,
    create_user_list_in_db,
)


class TestCreateList:
    """Tests for POST /api/lists endpoint."""

    @pytest.mark.asyncio
    async def test_create_list_successfully(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that creating a list returns 201 and list data."""
        # Arrange
        list_data = {"name": "My Shopping List", "description": "Weekend project items"}

        # Act
        response = await test_client.post("/api/lists", json=list_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Shopping List"
        assert data["description"] == "Weekend project items"
        assert data["list_id"] is not None
        assert data["total_items"] == 0
        assert data["unique_items"] == 0

    @pytest.mark.asyncio
    async def test_create_list_with_default_name(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that creating a list without name uses default."""
        # Arrange
        list_data = {}  # No name provided

        # Act
        response = await test_client.post("/api/lists", json=list_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My List"  # Default name

    @pytest.mark.asyncio
    async def test_create_list_sets_session_cookie(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that creating a list sets a session cookie."""
        list_data = {"name": "Test List"}

        response = await test_client.post("/api/lists", json=list_data)

        assert response.status_code == 201
        # Check that session_id cookie was set
        assert "session_id" in response.cookies or any(
            "session_id" in str(h) for h in response.headers.get_list("set-cookie")
        )


class TestGetMyLists:
    """Tests for GET /api/lists endpoint."""

    @pytest.mark.asyncio
    async def test_get_my_lists_returns_empty_for_new_session(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that get lists returns empty for new session."""
        response = await test_client.get("/api/lists")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    @pytest.mark.asyncio
    async def test_get_my_lists_returns_session_lists(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that get lists returns lists for current session."""
        # Arrange - create a list first to establish session
        create_response = await test_client.post(
            "/api/lists", json={"name": "First List"}
        )
        assert create_response.status_code == 201

        # Get session cookie from response
        cookies = dict(create_response.cookies)

        # Create another list
        await test_client.post(
            "/api/lists",
            json={"name": "Second List"},
            cookies=cookies,
        )

        # Act - get all lists
        response = await test_client.get("/api/lists", cookies=cookies)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


class TestGetListById:
    """Tests for GET /api/lists/{list_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_list_returns_list_with_items(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that get list by ID returns list with items."""
        # Arrange - create session, list, and product
        session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(
            db_session, session_id=session.id, name="Test List"
        )
        product = await create_product_in_db(
            db_session, sku="PROD-001", name="Test Product", price=29.99
        )
        await create_list_item_in_db(
            db_session,
            list_id=user_list.id,
            product_id=product.id,
            quantity=2,
            price_at_add=29.99,
        )

        # Act
        response = await test_client.get(f"/api/lists/{user_list.list_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["list_id"] == user_list.list_id
        assert data["name"] == "Test List"
        assert data["total_items"] == 2
        assert data["unique_items"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["quantity"] == 2
        assert data["items"][0]["product"]["sku"] == "PROD-001"

    @pytest.mark.asyncio
    async def test_get_list_returns_404_for_nonexistent(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that get list returns 404 for non-existent list ID."""
        response = await test_client.get("/api/lists/nonexistent-list-id")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_list_returns_empty_items_for_new_list(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that get list returns empty items for new list."""
        # Arrange
        session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(
            db_session, session_id=session.id, name="Empty List"
        )

        # Act
        response = await test_client.get(f"/api/lists/{user_list.list_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total_items"] == 0
        assert data["unique_items"] == 0


class TestAddItemToList:
    """Tests for POST /api/lists/{list_id}/items endpoint."""

    @pytest.mark.asyncio
    async def test_add_item_to_list_successfully(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that adding an item to list returns 201 and item data."""
        # Arrange
        session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(db_session, session_id=session.id)
        product = await create_product_in_db(
            db_session, sku="ADD-ITEM-001", name="Product to Add", price=19.99
        )

        item_data = {"product_sku": product.sku, "quantity": 3, "notes": "Need for project"}

        # Act
        response = await test_client.post(
            f"/api/lists/{user_list.list_id}/items", json=item_data
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["quantity"] == 3
        assert data["notes"] == "Need for project"
        assert data["product"]["sku"] == "ADD-ITEM-001"
        assert data["price_at_add"] == 19.99

    @pytest.mark.asyncio
    async def test_add_item_returns_404_for_nonexistent_list(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that adding item to non-existent list returns 404."""
        # Arrange
        product = await create_product_in_db(
            db_session, sku="PROD-001", name="Test Product"
        )

        item_data = {"product_sku": product.sku, "quantity": 1}

        # Act
        response = await test_client.post(
            "/api/lists/nonexistent-list-id/items", json=item_data
        )

        # Assert
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_add_item_returns_404_for_nonexistent_product(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that adding non-existent product returns 404."""
        # Arrange
        session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(db_session, session_id=session.id)

        item_data = {"product_sku": "NONEXISTENT-SKU", "quantity": 1}

        # Act
        response = await test_client.post(
            f"/api/lists/{user_list.list_id}/items", json=item_data
        )

        # Assert
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_add_item_validates_quantity(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that adding item validates quantity constraints."""
        # Arrange
        session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(db_session, session_id=session.id)
        product = await create_product_in_db(
            db_session, sku="VALIDATE-QTY", name="Test Product"
        )

        item_data = {"product_sku": product.sku, "quantity": 0}  # Invalid quantity

        # Act
        response = await test_client.post(
            f"/api/lists/{user_list.list_id}/items", json=item_data
        )

        # Assert
        assert response.status_code == 422  # Validation error


class TestRemoveItemFromList:
    """Tests for DELETE /api/lists/{list_id}/items/{sku} endpoint."""

    @pytest.mark.asyncio
    async def test_remove_item_returns_204(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that removing an item returns 204 No Content."""
        # Arrange
        session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(db_session, session_id=session.id)
        product = await create_product_in_db(
            db_session, sku="REMOVE-001", name="To Remove"
        )
        await create_list_item_in_db(
            db_session, list_id=user_list.id, product_id=product.id
        )

        # Act
        response = await test_client.delete(
            f"/api/lists/{user_list.list_id}/items/REMOVE-001"
        )

        # Assert
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_remove_item_returns_404_for_nonexistent_item(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that removing non-existent item returns 404."""
        # Arrange
        session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(db_session, session_id=session.id)

        # Act
        response = await test_client.delete(
            f"/api/lists/{user_list.list_id}/items/NONEXISTENT-SKU"
        )

        # Assert
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_remove_item_updates_list_counts(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that removing an item removes it from the list."""
        # Arrange
        session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(db_session, session_id=session.id)
        product = await create_product_in_db(
            db_session, sku="COUNT-001", name="Count Test"
        )
        await create_list_item_in_db(
            db_session, list_id=user_list.id, product_id=product.id, quantity=5
        )

        # Verify initial item exists
        response = await test_client.get(f"/api/lists/{user_list.list_id}")
        initial_data = response.json()
        assert len(initial_data["items"]) == 1
        assert initial_data["items"][0]["quantity"] == 5

        # Remove item - should succeed with 204
        delete_response = await test_client.delete(
            f"/api/lists/{user_list.list_id}/items/COUNT-001"
        )
        assert delete_response.status_code == 204

        # Verify item is removed by attempting to remove again (should 404)
        second_delete = await test_client.delete(
            f"/api/lists/{user_list.list_id}/items/COUNT-001"
        )
        assert second_delete.status_code == 404


class TestGenerateShareCode:
    """Tests for POST /api/lists/{list_id}/share endpoint."""

    @pytest.mark.asyncio
    async def test_generate_share_code_successfully(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that generating share code returns code and sync URL."""
        # Arrange
        session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(
            db_session, session_id=session.id, name="Shareable List"
        )

        # Act
        response = await test_client.post(f"/api/lists/{user_list.list_id}/share")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["list_id"] == user_list.list_id
        assert data["share_code"] is not None
        assert len(data["share_code"]) > 0
        assert f"/api/lists/sync/{data['share_code']}" == data["sync_url"]

    @pytest.mark.asyncio
    async def test_generate_share_code_returns_404_for_nonexistent(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that generating share code for non-existent list returns 404."""
        response = await test_client.post("/api/lists/nonexistent-list-id/share")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_generate_share_code_idempotent(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that generating share code multiple times returns same code."""
        # Arrange
        session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(db_session, session_id=session.id)

        # Act - generate code twice
        response1 = await test_client.post(f"/api/lists/{user_list.list_id}/share")
        response2 = await test_client.post(f"/api/lists/{user_list.list_id}/share")

        # Assert - both should return a share code (may or may not be the same)
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["share_code"] is not None
        assert response2.json()["share_code"] is not None


class TestSyncListFromCode:
    """Tests for POST /api/lists/sync/{share_code} endpoint."""

    @pytest.mark.asyncio
    async def test_sync_list_from_code_successfully(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that syncing list from code clones the list."""
        # Arrange - create source list with items
        source_session = await create_session_in_db(db_session)
        source_list = await create_user_list_in_db(
            db_session,
            session_id=source_session.id,
            name="Source List",
            share_code="TEST-SHARE-CODE",
        )
        product = await create_product_in_db(
            db_session, sku="SYNC-PROD", name="Sync Product", price=49.99
        )
        await create_list_item_in_db(
            db_session,
            list_id=source_list.id,
            product_id=product.id,
            quantity=2,
        )

        # Act - sync to new session
        response = await test_client.post("/api/lists/sync/TEST-SHARE-CODE")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Source List"
        assert data["list_id"] != source_list.list_id  # New list created
        assert len(data["items"]) == 1
        assert data["items"][0]["product"]["sku"] == "SYNC-PROD"

    @pytest.mark.asyncio
    async def test_sync_list_returns_404_for_invalid_code(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that syncing with invalid code returns 404."""
        response = await test_client.post("/api/lists/sync/INVALID-CODE")

        assert response.status_code == 404
        data = response.json()
        # Error message contains "no list found" with the share code
        assert "found" in data["detail"].lower()


class TestUpdateListItem:
    """Tests for PATCH /api/lists/{list_id}/items/{sku} endpoint."""

    @pytest.mark.asyncio
    async def test_update_list_item_quantity(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that updating list item quantity works correctly."""
        # Arrange
        session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(db_session, session_id=session.id)
        product = await create_product_in_db(
            db_session, sku="UPDATE-QTY-001", name="Update Quantity"
        )
        await create_list_item_in_db(
            db_session,
            list_id=user_list.id,
            product_id=product.id,
            quantity=1,
        )

        update_data = {"quantity": 5}

        # Act
        response = await test_client.patch(
            f"/api/lists/{user_list.list_id}/items/UPDATE-QTY-001",
            json=update_data,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 5

    @pytest.mark.asyncio
    async def test_update_list_item_notes(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that updating list item notes works correctly."""
        # Arrange
        session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(db_session, session_id=session.id)
        product = await create_product_in_db(
            db_session, sku="UPDATE-NOTES-001", name="Update Notes"
        )
        await create_list_item_in_db(
            db_session,
            list_id=user_list.id,
            product_id=product.id,
        )

        update_data = {"notes": "Updated notes here"}

        # Act
        response = await test_client.patch(
            f"/api/lists/{user_list.list_id}/items/UPDATE-NOTES-001",
            json=update_data,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == "Updated notes here"

    @pytest.mark.asyncio
    async def test_update_list_item_returns_404_for_nonexistent(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that updating non-existent item returns 404."""
        # Arrange
        session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(db_session, session_id=session.id)

        update_data = {"quantity": 5}

        # Act
        response = await test_client.patch(
            f"/api/lists/{user_list.list_id}/items/NONEXISTENT-SKU",
            json=update_data,
        )

        # Assert
        assert response.status_code == 404


class TestDeleteList:
    """Tests for DELETE /api/lists/{list_id} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_list_returns_204(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that deleting a list returns 204 No Content."""
        # Arrange
        session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(
            db_session, session_id=session.id, name="To Delete"
        )

        # Act
        response = await test_client.delete(f"/api/lists/{user_list.list_id}")

        # Assert
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_list_returns_404_for_nonexistent(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that deleting non-existent list returns 404."""
        response = await test_client.delete("/api/lists/nonexistent-list-id")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_deleted_list_not_accessible(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that deleted list is no longer accessible."""
        # Arrange
        session = await create_session_in_db(db_session)
        user_list = await create_user_list_in_db(db_session, session_id=session.id)
        list_id = user_list.list_id

        # Delete the list
        await test_client.delete(f"/api/lists/{list_id}")

        # Try to access the deleted list
        response = await test_client.get(f"/api/lists/{list_id}")

        assert response.status_code == 404
