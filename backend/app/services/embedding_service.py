"""Embedding service for generating vector embeddings."""

from functools import lru_cache
from typing import Protocol, runtime_checkable

from sentence_transformers import SentenceTransformer


@runtime_checkable
class ProductLike(Protocol):
    """Protocol for product-like objects."""

    name: str
    description: str | None
    short_description: str | None


class EmbeddingService:
    """Service for generating text embeddings using sentence-transformers."""

    MODEL_NAME = "all-MiniLM-L6-v2"
    VECTOR_SIZE = 384

    def __init__(self) -> None:
        """Initialize the embedding service with the model."""
        self._model: SentenceTransformer | None = None

    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the model on first use."""
        if self._model is None:
            self._model = SentenceTransformer(self.MODEL_NAME)
        return self._model

    def generate_embedding(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text to embed

        Returns:
            384-dimensional embedding vector
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def batch_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of input texts

        Returns:
            List of 384-dimensional embedding vectors
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return [emb.tolist() for emb in embeddings]

    def get_product_text(
        self, product: ProductLike, category_names: list[str] | None = None
    ) -> str:
        """
        Generate text representation of a product for embedding.

        Combines product name, description, and category names.

        Args:
            product: Product-like object with name, description fields
            category_names: Optional list of category names

        Returns:
            Combined text for embedding
        """
        parts = [product.name]

        if product.description:
            parts.append(product.description)
        elif product.short_description:
            parts.append(product.short_description)

        if category_names:
            parts.append(f"Categories: {', '.join(category_names)}")

        return ". ".join(parts)


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    """Get cached embedding service instance."""
    return EmbeddingService()
