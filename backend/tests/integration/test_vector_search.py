"""Integration tests for vector search flow."""

import pytest
from unittest.mock import MagicMock, patch


class TestVectorSearchIntegration:
    """Integration tests for the full vector search flow."""

    def test_embedding_service_generates_valid_vectors(self):
        """Test that real embedding service produces valid vectors."""
        from app.services.embedding_service import EmbeddingService

        service = EmbeddingService()

        # Test single embedding
        embedding = service.generate_embedding("cordless drill for concrete")
        assert len(embedding) == 384
        assert all(isinstance(x, float) for x in embedding)

        # Test batch embedding
        texts = ["hammer", "screwdriver", "saw"]
        embeddings = service.batch_embeddings(texts)
        assert len(embeddings) == 3
        assert all(len(e) == 384 for e in embeddings)

    def test_similar_products_have_higher_similarity(self):
        """Test that semantically similar products have higher cosine similarity."""
        import numpy as np
        from app.services.embedding_service import EmbeddingService

        service = EmbeddingService()

        # Generate embeddings for related and unrelated products
        drill_emb = np.array(service.generate_embedding("cordless power drill for drilling holes"))
        hammer_drill_emb = np.array(service.generate_embedding("hammer drill for concrete and masonry"))
        garden_chair_emb = np.array(service.generate_embedding("wooden garden chair for outdoor patio"))

        # Calculate cosine similarities
        def cosine_sim(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        drill_to_hammer = cosine_sim(drill_emb, hammer_drill_emb)
        drill_to_chair = cosine_sim(drill_emb, garden_chair_emb)

        # Drill should be more similar to hammer drill than to garden chair
        assert drill_to_hammer > drill_to_chair
        assert drill_to_hammer > 0.5  # Should have reasonable similarity

    def test_qdrant_service_crud_operations(self):
        """Test Qdrant service with mocked client."""
        from app.services.qdrant_service import QdrantService

        mock_client = MagicMock()
        mock_client.collection_exists.return_value = False

        service = QdrantService(client=mock_client)

        # Test collection creation
        service.ensure_collection()
        mock_client.create_collection.assert_called_once()

        # Test upsert
        service.upsert_product("SKU-001", [0.1] * 384, {"name": "Test"})
        mock_client.upsert.assert_called_once()

        # Test search
        mock_client.search.return_value = [
            MagicMock(payload={"sku": "SKU-001"}, score=0.9)
        ]
        results = service.search([0.1] * 384, limit=10)
        assert results == [("SKU-001", 0.9)]

        # Test delete
        service.delete_product("SKU-001")
        mock_client.delete.assert_called_once()
