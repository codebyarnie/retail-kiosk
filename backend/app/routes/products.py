"""Product API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.schemas.product import (
    ProductCreate,
    ProductDetailResponse,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from app.services.product_service import ProductService

router = APIRouter(prefix="/products")


@router.get("", response_model=ProductListResponse)
async def list_products(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    category_id: int | None = Query(default=None, description="Filter by category"),
    featured: bool = Query(default=False, description="Show featured products only"),
    db: AsyncSession = Depends(get_db),
) -> ProductListResponse:
    """
    List all products with pagination and filtering.

    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **category_id**: Optional category filter
    - **featured**: Show only featured products
    """
    service = ProductService(db)
    skip = (page - 1) * page_size

    products, total = await service.list_products(
        skip=skip,
        limit=page_size,
        category_id=category_id,
        featured_only=featured,
    )

    pages = (total + page_size - 1) // page_size if total > 0 else 1

    return ProductListResponse(
        items=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/featured", response_model=list[ProductResponse])
async def get_featured_products(
    limit: int = Query(default=10, ge=1, le=50, description="Number of products"),
    db: AsyncSession = Depends(get_db),
) -> list[ProductResponse]:
    """Get featured products for homepage display."""
    service = ProductService(db)
    products = await service.get_featured_products(limit=limit)
    return [ProductResponse.model_validate(p) for p in products]


@router.get("/{sku}", response_model=ProductDetailResponse)
async def get_product(
    sku: str,
    db: AsyncSession = Depends(get_db),
) -> ProductDetailResponse:
    """
    Get detailed product information by SKU.

    - **sku**: Product SKU (unique identifier)
    """
    service = ProductService(db)
    product = await service.get_product_by_sku(sku)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU '{sku}' not found",
        )

    return ProductDetailResponse.model_validate(product)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    """
    Create a new product.

    Requires admin authentication (TODO: implement auth).
    """
    service = ProductService(db)

    # Check if SKU already exists
    existing = await service.get_product_by_sku(product_data.sku)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with SKU '{product_data.sku}' already exists",
        )

    product = await service.create_product(product_data)
    return ProductResponse.model_validate(product)


@router.patch("/{sku}", response_model=ProductResponse)
async def update_product(
    sku: str,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    """
    Update an existing product.

    Requires admin authentication (TODO: implement auth).
    """
    service = ProductService(db)
    product = await service.get_product_by_sku(sku)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU '{sku}' not found",
        )

    updated = await service.update_product(product.id, product_data)
    return ProductResponse.model_validate(updated)


@router.delete("/{sku}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    sku: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a product (soft delete).

    Requires admin authentication (TODO: implement auth).
    """
    service = ProductService(db)
    product = await service.get_product_by_sku(sku)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU '{sku}' not found",
        )

    await service.delete_product(product.id)
