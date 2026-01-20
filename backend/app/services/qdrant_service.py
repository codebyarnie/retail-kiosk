"""Qdrant vector database service."""

import hashlib
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models

from app.config import settings


class QdrantService:
    """Service for interacting with Qdrant vector database."""

    COLLECTION_NAME = "products"
    VECTOR_SIZE = 384

    def __init__(self, client: QdrantClient | None = None) -> None:
        """
        Initialize the Qdrant service.

        Args:
            client: Optional QdrantClient instance (for testing)
        """
        self._client = client

    @property
    def client(self) -> QdrantClient:
        """Get or create Qdrant client."""
        if self._client is None:
            self._client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
                api_key=settings.qdrant_api_key,
                prefer_grpc=settings.qdrant_prefer_grpc,
            )
        return self._client

    def _sku_to_point_id(self, sku: str) -> str:
        """Convert SKU to a valid Qdrant point ID (UUID-like)."""
        hash_bytes = hashlib.md5(sku.encode()).hexdigest()
        return f"{hash_bytes[:8]}-{hash_bytes[8:12]}-{hash_bytes[12:16]}-{hash_bytes[16:20]}-{hash_bytes[20:32]}"

    def ensure_collection(self) -> None:
        """Create the products collection if it doesn't exist."""
        if self.client.collection_exists(self.COLLECTION_NAME):
            return

        self.client.create_collection(
            collection_name=self.COLLECTION_NAME,
            vectors_config=qdrant_models.VectorParams(
                size=self.VECTOR_SIZE,
                distance=qdrant_models.Distance.COSINE,
            ),
        )

    def upsert_product(
        self,
        sku: str,
        embedding: list[float],
        payload: dict[str, Any] | None = None,
    ) -> None:
        """
        Upsert a product vector to Qdrant.

        Args:
            sku: Product SKU (used as point ID)
            embedding: 384-dimensional embedding vector
            payload: Additional metadata (name, price, category_ids)
        """
        point_id = self._sku_to_point_id(sku)
        point_payload = payload or {}
        point_payload["sku"] = sku

        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=[
                qdrant_models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=point_payload,
                )
            ],
        )

    def search(
        self,
        query_embedding: list[float],
        limit: int = 20,
        price_min: float | None = None,
        price_max: float | None = None,
        category_ids: list[int] | None = None,
    ) -> list[tuple[str, float]]:
        """
        Search for similar products.

        Args:
            query_embedding: Query vector
            limit: Maximum results to return
            price_min: Optional minimum price filter
            price_max: Optional maximum price filter
            category_ids: Optional category filter

        Returns:
            List of (sku, score) tuples
        """
        must_conditions = []

        if price_min is not None:
            must_conditions.append(
                qdrant_models.FieldCondition(
                    key="price",
                    range=qdrant_models.Range(gte=price_min),
                )
            )

        if price_max is not None:
            must_conditions.append(
                qdrant_models.FieldCondition(
                    key="price",
                    range=qdrant_models.Range(lte=price_max),
                )
            )

        if category_ids:
            must_conditions.append(
                qdrant_models.FieldCondition(
                    key="category_ids",
                    match=qdrant_models.MatchAny(any=category_ids),
                )
            )

        query_filter = None
        if must_conditions:
            query_filter = qdrant_models.Filter(must=must_conditions)

        results = self.client.search(
            collection_name=self.COLLECTION_NAME,
            query_vector=query_embedding,
            limit=limit,
            query_filter=query_filter,
        )

        return [(hit.payload["sku"], hit.score) for hit in results]

    def delete_product(self, sku: str) -> None:
        """
        Delete a product vector from Qdrant.

        Args:
            sku: Product SKU to delete
        """
        point_id = self._sku_to_point_id(sku)

        self.client.delete(
            collection_name=self.COLLECTION_NAME,
            points_selector=qdrant_models.PointIdsList(points=[point_id]),
        )

    def get_all_skus(self) -> set[str]:
        """Get all SKUs currently in the collection."""
        skus: set[str] = set()
        offset = None

        while True:
            results, offset = self.client.scroll(
                collection_name=self.COLLECTION_NAME,
                limit=100,
                offset=offset,
                with_payload=["sku"],
            )

            for point in results:
                if "sku" in point.payload:
                    skus.add(point.payload["sku"])

            if offset is None:
                break

        return skus
