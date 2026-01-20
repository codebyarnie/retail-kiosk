# Vector Search & Embeddings Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Enable semantic product search using sentence-transformers embeddings stored in Qdrant, with Celery background tasks for data sync.

**Architecture:** EmbeddingService generates 384-dim vectors using all-MiniLM-L6-v2. Celery worker syncs products from JSON to PostgreSQL and Qdrant. SearchService queries Qdrant for semantic matches with keyword fallback.

**Tech Stack:** sentence-transformers, qdrant-client, Celery, Redis

**Design doc:** `docs/plans/2026-01-20-vector-search-design.md`

---

### Task 1: Add Dependencies

**Files:**
- Modify: `backend/requirements.txt`

**Step 1: Add sentence-transformers to requirements**

Add to `backend/requirements.txt`:
```
sentence-transformers>=2.2.0
```

**Step 2: Install dependencies**

Run: `cd backend && pip install -r requirements.txt`
Expected: Successfully installed sentence-transformers and dependencies

**Step 3: Verify import works**

Run: `cd backend && python -c "from sentence_transformers import SentenceTransformer; print('OK')"`
Expected: `OK`

**Step 4: Commit**

```bash
git add backend/requirements.txt
git commit -m "feat(backend): add sentence-transformers dependency"
```

---

### Task 2: Create EmbeddingService

**Files:**
- Create: `backend/app/services/embedding_service.py`
- Create: `backend/tests/services/test_embedding_service.py`

**Step 1: Write the failing test**

Create `backend/tests/services/__init__.py` (empty file if not exists).

Create `backend/tests/services/test_embedding_service.py`:
```python
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
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/services/test_embedding_service.py -v`
Expected: FAIL with "ModuleNotFoundError" or "cannot import name 'EmbeddingService'"

**Step 3: Write minimal implementation**

Create `backend/app/services/embedding_service.py`:
```python
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
```

**Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/services/test_embedding_service.py -v`
Expected: All 4 tests PASS

**Step 5: Commit**

```bash
git add backend/app/services/embedding_service.py backend/tests/services/
git commit -m "feat(backend): add EmbeddingService with sentence-transformers"
```

---

### Task 3: Create Qdrant Collection Manager

**Files:**
- Create: `backend/app/services/qdrant_service.py`
- Create: `backend/tests/services/test_qdrant_service.py`

**Step 1: Write the failing test**

Create `backend/tests/services/test_qdrant_service.py`:
```python
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
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/services/test_qdrant_service.py -v`
Expected: FAIL with "cannot import name 'QdrantService'"

**Step 3: Write minimal implementation**

Create `backend/app/services/qdrant_service.py`:
```python
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
        # Create a deterministic UUID from SKU
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
        # Build filter conditions
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
        skus = set()
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
```

**Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/services/test_qdrant_service.py -v`
Expected: All 5 tests PASS

**Step 5: Commit**

```bash
git add backend/app/services/qdrant_service.py backend/tests/services/test_qdrant_service.py
git commit -m "feat(backend): add QdrantService for vector storage"
```

---

### Task 4: Create Celery App Configuration

**Files:**
- Create: `backend/app/worker/__init__.py`
- Create: `backend/app/worker/celery_app.py`

**Step 1: Create worker package**

Create `backend/app/worker/__init__.py`:
```python
"""Celery worker package."""

from .celery_app import celery_app

__all__ = ["celery_app"]
```

**Step 2: Create Celery app configuration**

Create `backend/app/worker/celery_app.py`:
```python
"""Celery application configuration."""

from celery import Celery

from app.config import settings

celery_app = Celery(
    "retail_kiosk_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.worker.tasks"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer=settings.celery_task_serializer,
    result_serializer=settings.celery_result_serializer,
    accept_content=settings.celery_accept_content,
    timezone=settings.celery_timezone,
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)
```

**Step 3: Verify import works**

Run: `cd backend && python -c "from app.worker import celery_app; print(celery_app.main)"`
Expected: `retail_kiosk_worker`

**Step 4: Commit**

```bash
git add backend/app/worker/
git commit -m "feat(backend): add Celery app configuration"
```

---

### Task 5: Create Celery Tasks

**Files:**
- Create: `backend/app/worker/tasks.py`
- Create: `backend/tests/worker/__init__.py`
- Create: `backend/tests/worker/test_tasks.py`

**Step 1: Write the failing test**

Create `backend/tests/worker/__init__.py` (empty).

Create `backend/tests/worker/test_tasks.py`:
```python
"""Tests for Celery tasks."""

import json
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from pathlib import Path


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

        with patch("app.worker.tasks.get_sync_db_session") as mock_get_db, \
             patch("app.worker.tasks.update_product_embeddings") as mock_update:

            mock_session = MagicMock()
            mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_get_db.return_value.__exit__ = MagicMock(return_value=False)

            from app.worker.tasks import sync_product_data
            result = sync_product_data(str(json_file))

            assert result["processed"] == 1
            assert result["skus"] == ["TEST-001"]


class TestUpdateProductEmbeddingsTask:
    """Tests for update_product_embeddings task."""

    def test_update_embeddings_generates_and_upserts(self):
        """Test embedding generation and Qdrant upsert."""
        with patch("app.worker.tasks.get_sync_db_session") as mock_get_db, \
             patch("app.worker.tasks.get_embedding_service") as mock_get_emb, \
             patch("app.worker.tasks.QdrantService") as mock_qdrant_cls:

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

            from app.worker.tasks import update_product_embeddings
            result = update_product_embeddings("TEST-001")

            assert result["sku"] == "TEST-001"
            assert result["status"] == "updated"
            mock_qdrant.upsert_product.assert_called_once()


class TestCleanupStaleVectorsTask:
    """Tests for cleanup_stale_vectors task."""

    def test_cleanup_removes_vectors_for_deleted_products(self):
        """Test that vectors for non-existent products are removed."""
        with patch("app.worker.tasks.get_sync_db_session") as mock_get_db, \
             patch("app.worker.tasks.QdrantService") as mock_qdrant_cls:

            mock_session = MagicMock()
            mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_get_db.return_value.__exit__ = MagicMock(return_value=False)

            # DB has SKU-001, Qdrant has SKU-001 and SKU-002
            mock_session.execute.return_value.scalars.return_value.all.return_value = ["SKU-001"]

            mock_qdrant = MagicMock()
            mock_qdrant.get_all_skus.return_value = {"SKU-001", "SKU-002"}
            mock_qdrant_cls.return_value = mock_qdrant

            from app.worker.tasks import cleanup_stale_vectors
            result = cleanup_stale_vectors()

            assert result["deleted"] == 1
            assert "SKU-002" in result["deleted_skus"]
            mock_qdrant.delete_product.assert_called_once_with("SKU-002")
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/worker/test_tasks.py -v`
Expected: FAIL with "cannot import name 'sync_product_data'"

**Step 3: Write minimal implementation**

Create `backend/app/worker/tasks.py`:
```python
"""Celery tasks for product data sync and embedding generation."""

import json
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.models import Category, Product, ProductCategory
from app.services.embedding_service import get_embedding_service
from app.services.qdrant_service import QdrantService
from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)

# Sync engine for Celery tasks (not async)
_sync_engine = None
_sync_session_factory = None


def get_sync_engine():
    """Get synchronous database engine."""
    global _sync_engine
    if _sync_engine is None:
        _sync_engine = create_engine(settings.database_sync_url)
    return _sync_engine


def get_sync_session_factory():
    """Get synchronous session factory."""
    global _sync_session_factory
    if _sync_session_factory is None:
        _sync_session_factory = sessionmaker(bind=get_sync_engine())
    return _sync_session_factory


@contextmanager
def get_sync_db_session() -> Generator[Session, None, None]:
    """Get a synchronous database session for Celery tasks."""
    session = get_sync_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@celery_app.task(bind=True, max_retries=3)
def sync_product_data(self, file_path: str) -> dict[str, Any]:
    """
    Sync products from JSON file to database.

    Args:
        file_path: Path to products JSON file

    Returns:
        Dict with processed count and SKUs
    """
    try:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Products file not found: {file_path}")

        with open(path) as f:
            data = json.load(f)

        products_data = data.get("products", [])
        processed_skus = []

        with get_sync_db_session() as session:
            for product_data in products_data:
                sku = product_data["sku"]

                # Find or create product
                product = session.execute(
                    select(Product).where(Product.sku == sku)
                ).scalar_one_or_none()

                if product is None:
                    product = Product(sku=sku)
                    session.add(product)

                # Update product fields
                product.name = product_data["name"]
                product.description = product_data.get("description")
                product.short_description = product_data.get("short_description")
                product.price = product_data["price"]
                product.image_url = product_data.get("image_url")
                product.attributes = product_data.get("attributes", {})
                product.is_active = True

                # Handle categories
                category_slugs = product_data.get("categories", [])
                if category_slugs:
                    # Clear existing categories
                    session.execute(
                        ProductCategory.__table__.delete().where(
                            ProductCategory.product_id == product.id
                        )
                    ) if product.id else None

                    session.flush()  # Get product ID

                    for slug in category_slugs:
                        category = session.execute(
                            select(Category).where(Category.slug == slug)
                        ).scalar_one_or_none()

                        if category:
                            pc = ProductCategory(
                                product_id=product.id,
                                category_id=category.id
                            )
                            session.add(pc)

                processed_skus.append(sku)

        # Queue embedding updates for all processed products
        for sku in processed_skus:
            update_product_embeddings.delay(sku)

        logger.info(f"Synced {len(processed_skus)} products from {file_path}")
        return {"processed": len(processed_skus), "skus": processed_skus}

    except Exception as exc:
        logger.error(f"Failed to sync products: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def update_product_embeddings(self, sku: str | None = None) -> dict[str, Any]:
    """
    Update embeddings for one or all products.

    Args:
        sku: Optional SKU to update (None = all products)

    Returns:
        Dict with status and updated SKU(s)
    """
    try:
        embedding_service = get_embedding_service()
        qdrant_service = QdrantService()
        qdrant_service.ensure_collection()

        with get_sync_db_session() as session:
            if sku:
                # Single product update
                product = session.execute(
                    select(Product).where(Product.sku == sku)
                ).scalar_one_or_none()

                if not product:
                    return {"sku": sku, "status": "not_found"}

                _update_single_product_embedding(
                    session, product, embedding_service, qdrant_service
                )
                return {"sku": sku, "status": "updated"}

            else:
                # Update all products
                products = session.execute(
                    select(Product).where(Product.is_active == True)
                ).scalars().all()

                updated = []
                for product in products:
                    _update_single_product_embedding(
                        session, product, embedding_service, qdrant_service
                    )
                    updated.append(product.sku)

                return {"status": "updated_all", "count": len(updated), "skus": updated}

    except Exception as exc:
        logger.error(f"Failed to update embeddings: {exc}")
        raise self.retry(exc=exc, countdown=30)


def _update_single_product_embedding(
    session: Session,
    product: Product,
    embedding_service,
    qdrant_service: QdrantService,
) -> None:
    """Update embedding for a single product."""
    # Get category names
    category_names = []
    for pc in product.categories:
        if pc.category:
            category_names.append(pc.category.name)

    # Generate text and embedding
    text = embedding_service.get_product_text(product, category_names=category_names)
    embedding = embedding_service.generate_embedding(text)

    # Prepare payload
    category_ids = [pc.category_id for pc in product.categories]
    payload = {
        "name": product.name,
        "price": float(product.price) if product.price else 0.0,
        "category_ids": category_ids,
    }

    # Upsert to Qdrant
    qdrant_service.upsert_product(
        sku=product.sku,
        embedding=embedding,
        payload=payload,
    )


@celery_app.task(bind=True)
def cleanup_stale_vectors(self) -> dict[str, Any]:
    """
    Remove vectors for products that no longer exist in the database.

    Returns:
        Dict with count of deleted vectors
    """
    try:
        qdrant_service = QdrantService()

        with get_sync_db_session() as session:
            # Get all SKUs from database
            db_skus = set(
                session.execute(select(Product.sku)).scalars().all()
            )

            # Get all SKUs from Qdrant
            qdrant_skus = qdrant_service.get_all_skus()

            # Find stale SKUs (in Qdrant but not in DB)
            stale_skus = qdrant_skus - db_skus

            # Delete stale vectors
            for sku in stale_skus:
                qdrant_service.delete_product(sku)

            logger.info(f"Cleaned up {len(stale_skus)} stale vectors")
            return {"deleted": len(stale_skus), "deleted_skus": list(stale_skus)}

    except Exception as exc:
        logger.error(f"Failed to cleanup stale vectors: {exc}")
        raise
```

**Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/worker/test_tasks.py -v`
Expected: All 3 tests PASS

**Step 5: Commit**

```bash
git add backend/app/worker/tasks.py backend/tests/worker/
git commit -m "feat(backend): add Celery tasks for product sync and embeddings"
```

---

### Task 6: Update SearchService for Semantic Search

**Files:**
- Modify: `backend/app/services/search_service.py`
- Create: `backend/tests/services/test_search_service.py`

**Step 1: Write the failing test**

Create `backend/tests/services/test_search_service.py`:
```python
"""Tests for SearchService semantic search."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock


class TestSemanticSearch:
    """Tests for semantic search functionality."""

    @pytest.mark.asyncio
    async def test_semantic_search_uses_qdrant_when_available(self):
        """Test that semantic search queries Qdrant and returns products."""
        from app.services.search_service import SearchService

        # Mock database session
        mock_db = MagicMock()
        mock_db.execute = AsyncMock()

        # Mock product
        mock_product = MagicMock()
        mock_product.sku = "TEST-001"
        mock_product.name = "Test Product"
        mock_db.execute.return_value.scalars.return_value.all.return_value = [mock_product]

        service = SearchService(mock_db)

        with patch.object(service, "qdrant_client") as mock_qdrant, \
             patch("app.services.search_service.get_embedding_service") as mock_get_emb, \
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

            assert len(results) == 1
            assert results[0][0].sku == "TEST-001"
            assert results[0][1] == 0.95

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
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/services/test_search_service.py -v`
Expected: FAIL (semantic search not fully implemented)

**Step 3: Update implementation**

Modify `backend/app/services/search_service.py` - replace the `_semantic_search` method and add imports:

Add at top of file (after existing imports):
```python
from app.services.embedding_service import get_embedding_service
from app.services.qdrant_service import QdrantService
```

Replace the `_semantic_search` method (lines ~94-124):
```python
    async def _semantic_search(
        self,
        query: str,
        *,
        category_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        attributes: Optional[dict] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[tuple[Product, float]], int]:
        """
        Perform semantic search using Qdrant vector database.

        This method:
        1. Generates embedding for the query
        2. Searches Qdrant for similar product embeddings
        3. Applies filters (category, price, attributes)
        4. Returns products with relevance scores
        """
        # Generate query embedding
        embedding_service = get_embedding_service()
        query_embedding = embedding_service.generate_embedding(query)

        # Prepare category filter
        category_ids = None
        if category_id:
            category_ids = [category_id]

        # Search Qdrant
        qdrant_service = QdrantService()
        qdrant_results = qdrant_service.search(
            query_embedding=query_embedding,
            limit=limit + skip,  # Get extra for pagination
            price_min=min_price,
            price_max=max_price,
            category_ids=category_ids,
        )

        if not qdrant_results:
            return [], 0

        # Extract SKUs and scores
        sku_scores = {sku: score for sku, score in qdrant_results}
        skus = list(sku_scores.keys())

        # Fetch products from database
        products_query = select(Product).where(
            Product.sku.in_(skus),
            Product.is_active == True,
        )
        result = await self.db.execute(products_query)
        products = list(result.scalars().all())

        # Create product-score pairs maintaining Qdrant order
        scored_results = []
        for product in products:
            if product.sku in sku_scores:
                scored_results.append((product, sku_scores[product.sku]))

        # Sort by score descending
        scored_results.sort(key=lambda x: x[1], reverse=True)

        # Apply pagination
        total = len(scored_results)
        paginated = scored_results[skip : skip + limit]

        return paginated, total
```

**Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/services/test_search_service.py -v`
Expected: All 2 tests PASS

**Step 5: Commit**

```bash
git add backend/app/services/search_service.py backend/tests/services/test_search_service.py
git commit -m "feat(backend): implement semantic search with Qdrant"
```

---

### Task 7: Export Services in __init__.py

**Files:**
- Modify: `backend/app/services/__init__.py`

**Step 1: Update exports**

Add to `backend/app/services/__init__.py`:
```python
from .embedding_service import EmbeddingService, get_embedding_service
from .qdrant_service import QdrantService
```

**Step 2: Verify imports work**

Run: `cd backend && python -c "from app.services import EmbeddingService, QdrantService; print('OK')"`
Expected: `OK`

**Step 3: Commit**

```bash
git add backend/app/services/__init__.py
git commit -m "feat(backend): export embedding and qdrant services"
```

---

### Task 8: Create Sample Products JSON

**Files:**
- Create: `backend/data/products.json`

**Step 1: Create data directory**

Run: `mkdir -p backend/data`

**Step 2: Create sample products JSON**

Create `backend/data/products.json`:
```json
{
  "products": [
    {
      "sku": "DRL-001",
      "name": "DeWalt 20V MAX Hammer Drill",
      "description": "Powerful cordless hammer drill for drilling into concrete, brick, and masonry. Features 20V MAX battery system with long runtime.",
      "short_description": "20V cordless hammer drill for masonry",
      "price": 199.99,
      "categories": ["power-tools", "drills"],
      "image_url": "/images/drl-001.jpg",
      "attributes": {"voltage": "20V", "brand": "DeWalt", "type": "hammer"}
    },
    {
      "sku": "DRL-002",
      "name": "Makita 18V LXT Drill Driver",
      "description": "Compact and lightweight drill driver for everyday drilling and driving tasks. Variable speed trigger for precise control.",
      "short_description": "18V compact drill driver",
      "price": 149.99,
      "categories": ["power-tools", "drills"],
      "image_url": "/images/drl-002.jpg",
      "attributes": {"voltage": "18V", "brand": "Makita", "type": "driver"}
    },
    {
      "sku": "SAW-001",
      "name": "Milwaukee M18 Circular Saw",
      "description": "7-1/4 inch circular saw with brushless motor for efficient cuts through lumber and plywood. Includes blade guard and dust port.",
      "short_description": "18V brushless circular saw",
      "price": 229.99,
      "categories": ["power-tools", "saws"],
      "image_url": "/images/saw-001.jpg",
      "attributes": {"voltage": "18V", "brand": "Milwaukee", "blade_size": "7-1/4 inch"}
    },
    {
      "sku": "SAW-002",
      "name": "Bosch Jigsaw with T-Shank Blades",
      "description": "Versatile jigsaw for curved and straight cuts in wood, metal, and plastic. Low vibration design for comfortable use.",
      "short_description": "Corded jigsaw for precision cuts",
      "price": 129.99,
      "categories": ["power-tools", "saws"],
      "image_url": "/images/saw-002.jpg",
      "attributes": {"brand": "Bosch", "type": "jigsaw", "corded": true}
    },
    {
      "sku": "HMR-001",
      "name": "Estwing 16oz Claw Hammer",
      "description": "Professional grade steel claw hammer with shock-absorbing grip. Perfect for framing and general carpentry work.",
      "short_description": "16oz steel claw hammer",
      "price": 34.99,
      "categories": ["hand-tools", "hammers"],
      "image_url": "/images/hmr-001.jpg",
      "attributes": {"weight": "16oz", "brand": "Estwing", "material": "steel"}
    },
    {
      "sku": "HMR-002",
      "name": "Stanley FatMax Framing Hammer",
      "description": "Heavy-duty 22oz framing hammer with anti-vibration technology. Milled face for secure nail grip.",
      "short_description": "22oz framing hammer",
      "price": 44.99,
      "categories": ["hand-tools", "hammers"],
      "image_url": "/images/hmr-002.jpg",
      "attributes": {"weight": "22oz", "brand": "Stanley", "type": "framing"}
    },
    {
      "sku": "SCR-001",
      "name": "Klein Tools 11-in-1 Screwdriver",
      "description": "Multi-bit screwdriver with 11 different tips stored in the handle. Includes Phillips, slotted, square, and Torx bits.",
      "short_description": "11-in-1 multi-bit screwdriver",
      "price": 24.99,
      "categories": ["hand-tools", "screwdrivers"],
      "image_url": "/images/scr-001.jpg",
      "attributes": {"brand": "Klein Tools", "bits": 11}
    },
    {
      "sku": "MSR-001",
      "name": "Stanley 25ft PowerLock Tape Measure",
      "description": "Professional tape measure with 25 foot blade and blade lock. Wide blade stays rigid for long measurements.",
      "short_description": "25ft professional tape measure",
      "price": 19.99,
      "categories": ["hand-tools", "measuring"],
      "image_url": "/images/msr-001.jpg",
      "attributes": {"length": "25ft", "brand": "Stanley"}
    },
    {
      "sku": "SFT-001",
      "name": "3M WorkTunes Hearing Protector",
      "description": "Bluetooth hearing protection with AM/FM radio. Noise reduction rating of 24dB for loud work environments.",
      "short_description": "Bluetooth hearing protection headphones",
      "price": 54.99,
      "categories": ["safety", "hearing-protection"],
      "image_url": "/images/sft-001.jpg",
      "attributes": {"brand": "3M", "nrr": "24dB", "bluetooth": true}
    },
    {
      "sku": "SFT-002",
      "name": "Carhartt Insulated Work Gloves",
      "description": "Durable insulated work gloves with reinforced palm. Water-resistant and touchscreen compatible fingertips.",
      "short_description": "Insulated touchscreen work gloves",
      "price": 29.99,
      "categories": ["safety", "gloves"],
      "image_url": "/images/sft-002.jpg",
      "attributes": {"brand": "Carhartt", "insulated": true, "touchscreen": true}
    }
  ]
}
```

**Step 3: Commit**

```bash
git add backend/data/
git commit -m "feat(backend): add sample products JSON for sync task"
```

---

### Task 9: Add Admin Sync Endpoint

**Files:**
- Create: `backend/app/routes/admin.py`
- Modify: `backend/app/routes/__init__.py`
- Modify: `backend/app/main.py`

**Step 1: Create admin routes**

Create `backend/app/routes/admin.py`:
```python
"""Admin routes for data management."""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.worker.tasks import sync_product_data, update_product_embeddings, cleanup_stale_vectors

router = APIRouter(prefix="/admin", tags=["admin"])


class SyncRequest(BaseModel):
    """Request body for sync endpoint."""
    file_path: str | None = None


class TaskResponse(BaseModel):
    """Response for async task endpoints."""
    task_id: str
    status: str


@router.post("/sync-products", response_model=TaskResponse)
async def trigger_sync_products(request: SyncRequest | None = None):
    """
    Trigger product data sync from JSON file.

    Args:
        request: Optional file path (defaults to backend/data/products.json)

    Returns:
        Task ID for tracking
    """
    # Default to products.json in data directory
    if request and request.file_path:
        file_path = request.file_path
    else:
        file_path = str(Path(__file__).parent.parent.parent / "data" / "products.json")

    if not Path(file_path).exists():
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

    task = sync_product_data.delay(file_path)
    return TaskResponse(task_id=task.id, status="queued")


@router.post("/update-embeddings", response_model=TaskResponse)
async def trigger_update_embeddings(sku: str | None = None):
    """
    Trigger embedding update for one or all products.

    Args:
        sku: Optional SKU (None = update all)

    Returns:
        Task ID for tracking
    """
    task = update_product_embeddings.delay(sku)
    return TaskResponse(task_id=task.id, status="queued")


@router.post("/cleanup-vectors", response_model=TaskResponse)
async def trigger_cleanup_vectors():
    """
    Trigger cleanup of stale vectors.

    Returns:
        Task ID for tracking
    """
    task = cleanup_stale_vectors.delay()
    return TaskResponse(task_id=task.id, status="queued")
```

**Step 2: Export admin router**

Add to `backend/app/routes/__init__.py`:
```python
from .admin import router as admin_router
```

**Step 3: Register admin router in main.py**

Add to `backend/app/main.py` (after other router includes):
```python
from app.routes import admin_router
app.include_router(admin_router, prefix="/api")
```

**Step 4: Verify endpoint exists**

Run: `cd backend && python -c "from app.main import app; print([r.path for r in app.routes if 'admin' in r.path])"`
Expected: `['/api/admin/sync-products', '/api/admin/update-embeddings', '/api/admin/cleanup-vectors']`

**Step 5: Commit**

```bash
git add backend/app/routes/admin.py backend/app/routes/__init__.py backend/app/main.py
git commit -m "feat(backend): add admin endpoints for sync and embedding tasks"
```

---

### Task 10: Integration Test - Full Flow

**Files:**
- Create: `backend/tests/integration/test_vector_search.py`

**Step 1: Create integration test**

Create `backend/tests/integration/__init__.py` (empty).

Create `backend/tests/integration/test_vector_search.py`:
```python
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
```

**Step 2: Run integration tests**

Run: `cd backend && python -m pytest tests/integration/test_vector_search.py -v`
Expected: All 3 tests PASS

**Step 3: Commit**

```bash
git add backend/tests/integration/
git commit -m "test(backend): add integration tests for vector search"
```

---

### Task 11: Test with Running Services

**Step 1: Ensure Docker services are running**

Run: `docker-compose up -d`
Expected: postgres, redis, qdrant containers running

**Step 2: Check Qdrant health**

Run: `curl http://localhost:6333/healthz`
Expected: Response indicates healthy

**Step 3: Start Celery worker in background**

Run: `cd backend && celery -A app.worker.celery_app worker --loglevel=info &`
Expected: Worker starts and connects to Redis

**Step 4: Trigger product sync via API**

Run: `curl -X POST http://localhost:8000/api/admin/sync-products`
Expected: `{"task_id": "...", "status": "queued"}`

**Step 5: Wait for task completion and verify embeddings**

Run: `curl http://localhost:6333/collections/products`
Expected: Collection exists with points_count > 0

**Step 6: Test semantic search**

Run: `curl "http://localhost:8000/api/search?q=drill%20for%20concrete"`
Expected: Returns products with DeWalt hammer drill ranked high

**Step 7: Commit final state**

```bash
git add -A
git commit -m "feat(backend): complete Phase 3 vector search implementation"
```

---

## Summary

After completing all tasks:

1. **EmbeddingService** generates 384-dim vectors using all-MiniLM-L6-v2
2. **QdrantService** manages the products collection
3. **Celery tasks** sync products and update embeddings
4. **SearchService** performs semantic search with keyword fallback
5. **Admin endpoints** trigger sync and embedding tasks
6. **Integration tests** verify the full flow

Run all tests: `cd backend && python -m pytest -v`
