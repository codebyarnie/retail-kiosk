"""Celery tasks for product data sync and embedding generation."""

from __future__ import annotations

from contextlib import contextmanager
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.models import Category, Product, ProductCategory
from app.services.embedding_service import get_embedding_service
from app.services.qdrant_service import QdrantService
from app.worker.celery_app import celery_app

if TYPE_CHECKING:
    from collections.abc import Generator

    from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

# Sync engine for Celery tasks (not async)
_sync_engine = None
_sync_session_factory = None


def get_sync_engine():
    """Get synchronous database engine."""
    global _sync_engine  # noqa: PLW0603
    if _sync_engine is None:
        _sync_engine = create_engine(settings.database_sync_url)
    return _sync_engine


def get_sync_session_factory():
    """Get synchronous session factory."""
    global _sync_session_factory  # noqa: PLW0603
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


def _raise_file_not_found(file_path: str) -> None:
    """Raise FileNotFoundError for missing file."""
    msg = f"Products file not found: {file_path}"
    raise FileNotFoundError(msg)


@celery_app.task(bind=True, max_retries=3)
def sync_product_data(self, file_path: str) -> dict[str, Any]:
    """
    Sync products from JSON file to database.

    Args:
        self: Celery task instance
        file_path: Path to products JSON file

    Returns:
        Dict with processed count and SKUs
    """
    try:
        path = Path(file_path)
        if not path.exists():
            _raise_file_not_found(file_path)

        with path.open() as f:
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
                    if product.id:
                        session.execute(
                            ProductCategory.__table__.delete().where(
                                ProductCategory.product_id == product.id
                            )
                        )

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

        logger.info("Synced %d products from %s", len(processed_skus), file_path)
        return {"processed": len(processed_skus), "skus": processed_skus}

    except Exception as exc:
        logger.exception("Failed to sync products")
        raise self.retry(exc=exc, countdown=60) from exc


@celery_app.task(bind=True, max_retries=3)
def update_product_embeddings(self, sku: str | None = None) -> dict[str, Any]:
    """
    Update embeddings for one or all products.

    Args:
        self: Celery task instance
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
                    product, embedding_service, qdrant_service
                )
                return {"sku": sku, "status": "updated"}

            # Update all products
            products = session.execute(
                select(Product).where(Product.is_active.is_(True))
            ).scalars().all()

            updated = []
            for product in products:
                _update_single_product_embedding(
                    product, embedding_service, qdrant_service
                )
                updated.append(product.sku)

            return {"status": "updated_all", "count": len(updated), "skus": updated}

    except Exception as exc:
        logger.exception("Failed to update embeddings")
        raise self.retry(exc=exc, countdown=30) from exc


def _update_single_product_embedding(
    product: Product,
    embedding_service: EmbeddingService,
    qdrant_service: QdrantService,
) -> None:
    """Update embedding for a single product."""
    # Get category names
    category_names = [
        pc.category.name for pc in product.categories if pc.category
    ]

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
def cleanup_stale_vectors(self) -> dict[str, Any]:  # noqa: ARG001
    """
    Remove vectors for products that no longer exist in the database.

    Args:
        self: Celery task instance (unused but required for bind=True)

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

            logger.info("Cleaned up %d stale vectors", len(stale_skus))
            return {"deleted": len(stale_skus), "deleted_skus": list(stale_skus)}

    except Exception:
        logger.exception("Failed to cleanup stale vectors")
        raise
