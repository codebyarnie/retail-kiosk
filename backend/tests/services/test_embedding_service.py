"""Tests for EmbeddingService."""

import pytest


class TestEmbeddingService:
    """Test cases for EmbeddingService."""

    def test_generate_embedding_returns_correct_dimensions(self):
        """Test that generate_embedding returns 384-dim vector."""
        from app.services.embedding_service import EmbeddingService

        service = EmbeddingService()
        embedding = service.generate_embedding("test product")

        assert isinstance(embedding, list)
        assert len(embedding) == 384
        assert all(isinstance(x, float) for x in embedding)

    def test_generate_embedding_different_texts_produce_different_vectors(self):
        """Test that different texts produce different embeddings."""
        from app.services.embedding_service import EmbeddingService

        service = EmbeddingService()
        emb1 = service.generate_embedding("hammer drill for concrete")
        emb2 = service.generate_embedding("wooden garden chair")

        # Vectors should be different
        assert emb1 != emb2

    def test_batch_embeddings_returns_list_of_vectors(self):
        """Test batch embedding generation."""
        from app.services.embedding_service import EmbeddingService

        service = EmbeddingService()
        texts = ["product one", "product two", "product three"]
        embeddings = service.batch_embeddings(texts)

        assert len(embeddings) == 3
        assert all(len(emb) == 384 for emb in embeddings)

    def test_get_product_text_combines_fields(self):
        """Test product text generation for embedding."""
        from app.services.embedding_service import EmbeddingService

        service = EmbeddingService()

        # Mock product-like object
        class MockProduct:
            name = "DeWalt Hammer Drill"
            description = "Powerful cordless drill"
            short_description = "20V drill"

        text = service.get_product_text(MockProduct(), category_names=["Power Tools", "Drills"])

        assert "DeWalt Hammer Drill" in text
        assert "Powerful cordless drill" in text
        assert "Power Tools" in text
        assert "Drills" in text
