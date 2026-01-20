"""Tests for Celery tasks."""

import json
from unittest.mock import MagicMock, patch


class TestSyncProductDataTask:
    """Tests for sync_product_data task."""

    def test_sync_product_data_parses_json_and_upserts(self, tmp_path):
        """Test that sync_product_data reads JSON and creates products."""
        # Create test JSON file
        products_data = {
            "products": [
                {
                    "sku": "TEST-001",
                    "name": "Test Product",
                    "description": "A test product",
                    "price": 19.99,
                    "categories": ["tools"],
                }
            ]
        }
        json_file = tmp_path / "products.json"
        json_file.write_text(json.dumps(products_data))

        with (
            patch("app.worker.tasks.get_sync_db_session") as mock_get_db,
            patch("app.worker.tasks.update_product_embeddings"),
        ):
            mock_session = MagicMock()
            mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_get_db.return_value.__exit__ = MagicMock(return_value=False)

            # Import inside patch context to use mocked dependencies
            from app.worker.tasks import sync_product_data  # noqa: PLC0415

            result = sync_product_data(str(json_file))

            assert result["processed"] == 1
            assert result["skus"] == ["TEST-001"]


class TestUpdateProductEmbeddingsTask:
    """Tests for update_product_embeddings task."""

    def test_update_embeddings_generates_and_upserts(self):
        """Test embedding generation and Qdrant upsert."""
        with (
            patch("app.worker.tasks.get_sync_db_session") as mock_get_db,
            patch("app.worker.tasks.get_embedding_service") as mock_get_emb,
            patch("app.worker.tasks.QdrantService") as mock_qdrant_cls,
        ):
            # Setup mocks
            mock_session = MagicMock()
            mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_get_db.return_value.__exit__ = MagicMock(return_value=False)

            mock_product = MagicMock()
            mock_product.sku = "TEST-001"
            mock_product.name = "Test Product"
            mock_product.description = "Description"
            mock_product.short_description = None
            mock_product.price = 19.99
            mock_product.categories = []
            mock_session.execute.return_value.scalar_one_or_none.return_value = mock_product

            mock_emb_service = MagicMock()
            mock_emb_service.get_product_text.return_value = "Test Product. Description"
            mock_emb_service.generate_embedding.return_value = [0.1] * 384
            mock_get_emb.return_value = mock_emb_service

            mock_qdrant = MagicMock()
            mock_qdrant_cls.return_value = mock_qdrant

            # Import inside patch context to use mocked dependencies
            from app.worker.tasks import update_product_embeddings  # noqa: PLC0415

            result = update_product_embeddings("TEST-001")

            assert result["sku"] == "TEST-001"
            assert result["status"] == "updated"
            mock_qdrant.upsert_product.assert_called_once()

    def test_update_embeddings_extracts_category_names_and_ids_from_category_objects(self):
        """Test that category names and IDs are correctly extracted from Category objects.

        The Product.categories relationship returns Category objects directly (via secondary
        table), not ProductCategory association objects. This test verifies the fix for
        correctly accessing .name and .id attributes on Category objects.
        """
        with (
            patch("app.worker.tasks.get_sync_db_session") as mock_get_db,
            patch("app.worker.tasks.get_embedding_service") as mock_get_emb,
            patch("app.worker.tasks.QdrantService") as mock_qdrant_cls,
        ):
            # Setup mocks
            mock_session = MagicMock()
            mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_get_db.return_value.__exit__ = MagicMock(return_value=False)

            # Create mock Category objects (not ProductCategory association objects)
            mock_category_1 = MagicMock()
            mock_category_1.id = 1
            mock_category_1.name = "Tools"

            mock_category_2 = MagicMock()
            mock_category_2.id = 5
            mock_category_2.name = "Hardware"

            mock_product = MagicMock()
            mock_product.sku = "TEST-002"
            mock_product.name = "Power Drill"
            mock_product.description = "A powerful drill"
            mock_product.short_description = None
            mock_product.price = 99.99
            # product.categories returns Category objects directly
            mock_product.categories = [mock_category_1, mock_category_2]
            mock_session.execute.return_value.scalar_one_or_none.return_value = mock_product

            mock_emb_service = MagicMock()
            mock_emb_service.get_product_text.return_value = "Power Drill. A powerful drill"
            mock_emb_service.generate_embedding.return_value = [0.1] * 384
            mock_get_emb.return_value = mock_emb_service

            mock_qdrant = MagicMock()
            mock_qdrant_cls.return_value = mock_qdrant

            from app.worker.tasks import update_product_embeddings  # noqa: PLC0415

            result = update_product_embeddings("TEST-002")

            assert result["sku"] == "TEST-002"
            assert result["status"] == "updated"

            # Verify get_product_text was called with category names
            mock_emb_service.get_product_text.assert_called_once()
            call_kwargs = mock_emb_service.get_product_text.call_args
            assert call_kwargs[1]["category_names"] == ["Tools", "Hardware"]

            # Verify upsert_product was called with correct category IDs in payload
            mock_qdrant.upsert_product.assert_called_once()
            upsert_kwargs = mock_qdrant.upsert_product.call_args[1]
            assert upsert_kwargs["payload"]["category_ids"] == [1, 5]


class TestCleanupStaleVectorsTask:
    """Tests for cleanup_stale_vectors task."""

    def test_cleanup_removes_vectors_for_deleted_products(self):
        """Test that vectors for non-existent products are removed."""
        with (
            patch("app.worker.tasks.get_sync_db_session") as mock_get_db,
            patch("app.worker.tasks.QdrantService") as mock_qdrant_cls,
        ):
            mock_session = MagicMock()
            mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_get_db.return_value.__exit__ = MagicMock(return_value=False)

            # DB has SKU-001, Qdrant has SKU-001 and SKU-002
            mock_session.execute.return_value.scalars.return_value.all.return_value = ["SKU-001"]

            mock_qdrant = MagicMock()
            mock_qdrant.get_all_skus.return_value = {"SKU-001", "SKU-002"}
            mock_qdrant_cls.return_value = mock_qdrant

            # Import inside patch context to use mocked dependencies
            from app.worker.tasks import cleanup_stale_vectors  # noqa: PLC0415

            result = cleanup_stale_vectors()

            assert result["deleted"] == 1
            assert "SKU-002" in result["deleted_skus"]
            mock_qdrant.delete_product.assert_called_once_with("SKU-002")
