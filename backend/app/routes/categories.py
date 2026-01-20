"""Category API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryTreeResponse,
    CategoryUpdate,
    CategoryWithProducts,
)
from app.schemas.product import ProductResponse
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories")


@router.get("", response_model=list[CategoryResponse])
async def list_categories(
    root_only: bool = Query(
        default=False, description="Only return root-level categories"
    ),
    db: AsyncSession = Depends(get_db),
) -> list[CategoryResponse]:
    """
    List all active categories.

    - **root_only**: If true, only return categories without a parent
    """
    service = CategoryService(db)
    categories = await service.list_categories(root_only=root_only)
    return [CategoryResponse.model_validate(c) for c in categories]


@router.get("/tree", response_model=list[CategoryTreeResponse])
async def get_category_tree(
    db: AsyncSession = Depends(get_db),
) -> list[CategoryTreeResponse]:
    """Get full category tree with nested children."""
    service = CategoryService(db)
    categories = await service.get_category_tree()

    def build_tree(cat) -> CategoryTreeResponse:
        return CategoryTreeResponse(
            id=cat.id,
            name=cat.name,
            slug=cat.slug,
            description=cat.description,
            image_url=cat.image_url,
            parent_id=cat.parent_id,
            display_order=cat.display_order,
            is_active=cat.is_active,
            children=[build_tree(child) for child in cat.children if child.is_active],
        )

    return [build_tree(c) for c in categories]


@router.get("/{slug}", response_model=CategoryWithProducts)
async def get_category(
    slug: str,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
) -> CategoryWithProducts:
    """
    Get category details with its products.

    - **slug**: Category URL slug
    - **page**: Page number for products
    - **page_size**: Products per page
    """
    service = CategoryService(db)
    category = await service.get_category_by_slug(slug)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{slug}' not found",
        )

    skip = (page - 1) * page_size
    _, products, total = await service.get_category_with_products(
        category.id, skip=skip, limit=page_size
    )

    return CategoryWithProducts(
        id=category.id,
        name=category.name,
        slug=category.slug,
        description=category.description,
        image_url=category.image_url,
        parent_id=category.parent_id,
        display_order=category.display_order,
        is_active=category.is_active,
        products=[ProductResponse.model_validate(p) for p in products],
        product_count=total,
    )


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
) -> CategoryResponse:
    """
    Create a new category.

    Requires admin authentication (TODO: implement auth).
    """
    service = CategoryService(db)

    # Check if slug already exists
    existing = await service.get_category_by_slug(category_data.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category with slug '{category_data.slug}' already exists",
        )

    category = await service.create_category(category_data)
    return CategoryResponse.model_validate(category)


@router.patch("/{slug}", response_model=CategoryResponse)
async def update_category(
    slug: str,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
) -> CategoryResponse:
    """
    Update an existing category.

    Requires admin authentication (TODO: implement auth).
    """
    service = CategoryService(db)
    category = await service.get_category_by_slug(slug)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{slug}' not found",
        )

    updated = await service.update_category(category.id, category_data)
    return CategoryResponse.model_validate(updated)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a category (soft delete).

    Requires admin authentication (TODO: implement auth).
    """
    service = CategoryService(db)
    category = await service.get_category_by_slug(slug)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{slug}' not found",
        )

    await service.delete_category(category.id)
