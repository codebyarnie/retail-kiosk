"""Tests for SearchService semantic search."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock


class TestSemanticSearch:
    """Tests for semantic search functionality."""

    @pytest.mark.asyncio
    async def test_semantic_search_uses_qdrant_when_available(self):
        """Test that semantic search queries Qdrant and returns products."""
        from app.services.search_service import SearchService

        # Mock database session - need to match async SQLAlchemy patterns
        mock_db = MagicMock()

        # Mock product
        mock_product = MagicMock()
        mock_product.sku = "TEST-001"
        mock_product.name = "Test Product"

        # Mock the scalars result - SQLAlchemy uses result.scalars().all()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_product]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars

        # Make execute return a coroutine that resolves to mock_result
        mock_db.execute = AsyncMock(return_value=mock_result)

        service = SearchService(mock_db)

        with patch("app.services.search_service.get_embedding_service") as mock_get_emb, \
             patch("app.services.search_service.QdrantService") as mock_qdrant_svc_cls:

            # Setup Qdrant mock
            mock_qdrant_svc = MagicMock()
            mock_qdrant_svc.search.return_value = [("TEST-001", 0.95)]
            mock_qdrant_svc_cls.return_value = mock_qdrant_svc

            # Setup embedding mock
            mock_emb_service = MagicMock()
            mock_emb_service.generate_embedding.return_value = [0.1] * 384
            mock_get_emb.return_value = mock_emb_service

            results, total = await service._semantic_search("test query")

            # Verify embedding service was called
            mock_get_emb.assert_called_once()
            mock_emb_service.generate_embedding.assert_called_once_with("test query")

            # Verify Qdrant service was called
            mock_qdrant_svc_cls.assert_called_once()
            mock_qdrant_svc.search.assert_called_once()

            # Verify results
            assert len(results) == 1
            assert results[0][0].sku == "TEST-001"
            assert results[0][1] == 0.95

    @pytest.mark.asyncio
    async def test_semantic_search_returns_empty_when_qdrant_returns_no_results(self):
        """Test that semantic search returns empty list when Qdrant has no matches."""
        from app.services.search_service import SearchService

        mock_db = MagicMock()
        mock_db.execute = AsyncMock()

        service = SearchService(mock_db)

        with patch("app.services.search_service.get_embedding_service") as mock_get_emb, \
             patch("app.services.search_service.QdrantService") as mock_qdrant_svc_cls:

            # Setup Qdrant mock to return empty results
            mock_qdrant_svc = MagicMock()
            mock_qdrant_svc.search.return_value = []
            mock_qdrant_svc_cls.return_value = mock_qdrant_svc

            # Setup embedding mock
            mock_emb_service = MagicMock()
            mock_emb_service.generate_embedding.return_value = [0.1] * 384
            mock_get_emb.return_value = mock_emb_service

            results, total = await service._semantic_search("nonexistent query")

            assert len(results) == 0
            assert total == 0

    @pytest.mark.asyncio
    async def test_search_falls_back_to_keyword_on_qdrant_error(self):
        """Test fallback to keyword search when Qdrant fails."""
        from app.services.search_service import SearchService

        mock_db = MagicMock()
        mock_db.execute = AsyncMock()

        service = SearchService(mock_db)

        with patch.object(service, "_semantic_search", side_effect=Exception("Qdrant error")), \
             patch.object(service, "_keyword_search", new_callable=AsyncMock) as mock_keyword:

            mock_keyword.return_value = ([], 0)
            service._qdrant_client = MagicMock()  # Pretend Qdrant is available

            results, total = await service.search_products("test")

            mock_keyword.assert_called_once()

    @pytest.mark.asyncio
    async def test_semantic_search_applies_category_filter(self):
        """Test that semantic search passes category filter to Qdrant."""
        from app.services.search_service import SearchService

        mock_db = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute = AsyncMock(return_value=mock_result)

        service = SearchService(mock_db)

        with patch("app.services.search_service.get_embedding_service") as mock_get_emb, \
             patch("app.services.search_service.QdrantService") as mock_qdrant_svc_cls:

            mock_qdrant_svc = MagicMock()
            mock_qdrant_svc.search.return_value = []
            mock_qdrant_svc_cls.return_value = mock_qdrant_svc

            mock_emb_service = MagicMock()
            mock_emb_service.generate_embedding.return_value = [0.1] * 384
            mock_get_emb.return_value = mock_emb_service

            await service._semantic_search("drill", category_id=5)

            # Verify category_ids was passed to Qdrant search
            call_kwargs = mock_qdrant_svc.search.call_args.kwargs
            assert call_kwargs["category_ids"] == [5]

    @pytest.mark.asyncio
    async def test_semantic_search_applies_price_filters(self):
        """Test that semantic search passes price filters to Qdrant."""
        from app.services.search_service import SearchService

        mock_db = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute = AsyncMock(return_value=mock_result)

        service = SearchService(mock_db)

        with patch("app.services.search_service.get_embedding_service") as mock_get_emb, \
             patch("app.services.search_service.QdrantService") as mock_qdrant_svc_cls:

            mock_qdrant_svc = MagicMock()
            mock_qdrant_svc.search.return_value = []
            mock_qdrant_svc_cls.return_value = mock_qdrant_svc

            mock_emb_service = MagicMock()
            mock_emb_service.generate_embedding.return_value = [0.1] * 384
            mock_get_emb.return_value = mock_emb_service

            await service._semantic_search("tool", min_price=10.0, max_price=100.0)

            # Verify price filters were passed to Qdrant search
            call_kwargs = mock_qdrant_svc.search.call_args.kwargs
            assert call_kwargs["price_min"] == 10.0
            assert call_kwargs["price_max"] == 100.0
