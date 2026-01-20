"""Tests for QdrantService."""

import pytest
from unittest.mock import MagicMock, patch


class TestQdrantService:
    """Test cases for QdrantService."""

    def test_ensure_collection_creates_if_not_exists(self):
        """Test collection creation when it doesn't exist."""
        from app.services.qdrant_service import QdrantService

        mock_client = MagicMock()
        mock_client.collection_exists.return_value = False

        service = QdrantService(client=mock_client)
        service.ensure_collection()

        mock_client.collection_exists.assert_called_once_with("products")
        mock_client.create_collection.assert_called_once()

    def test_ensure_collection_skips_if_exists(self):
        """Test collection not recreated if exists."""
        from app.services.qdrant_service import QdrantService

        mock_client = MagicMock()
        mock_client.collection_exists.return_value = True

        service = QdrantService(client=mock_client)
        service.ensure_collection()

        mock_client.collection_exists.assert_called_once()
        mock_client.create_collection.assert_not_called()

    def test_upsert_product_vector(self):
        """Test upserting a product vector."""
        from app.services.qdrant_service import QdrantService

        mock_client = MagicMock()
        service = QdrantService(client=mock_client)

        service.upsert_product(
            sku="TEST-001",
            embedding=[0.1] * 384,
            payload={"name": "Test Product", "price": 9.99}
        )

        mock_client.upsert.assert_called_once()

    def test_search_returns_results(self):
        """Test vector search returns SKUs with scores."""
        from app.services.qdrant_service import QdrantService

        mock_client = MagicMock()
        mock_client.search.return_value = [
            MagicMock(payload={"sku": "SKU-001"}, score=0.95),
            MagicMock(payload={"sku": "SKU-002"}, score=0.80),
        ]

        service = QdrantService(client=mock_client)
        results = service.search([0.1] * 384, limit=10)

        assert len(results) == 2
        assert results[0] == ("SKU-001", 0.95)
        assert results[1] == ("SKU-002", 0.80)

    def test_delete_product_vector(self):
        """Test deleting a product vector."""
        from app.services.qdrant_service import QdrantService

        mock_client = MagicMock()
        service = QdrantService(client=mock_client)

        service.delete_product("TEST-001")

        mock_client.delete.assert_called_once()
