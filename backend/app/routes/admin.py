"""Admin routes for data management."""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.worker.tasks import cleanup_stale_vectors, sync_product_data, update_product_embeddings

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
