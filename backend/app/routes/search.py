"""Search API routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.schemas.product import ProductResponse
from app.schemas.search import (
    SearchResponse,
    SearchResult,
    SearchSuggestion,
    SearchSuggestionsResponse,
)
from app.services.search_service import SearchService

router = APIRouter(prefix="/search")


@router.get("", response_model=SearchResponse)
async def search_products(
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    category_id: int | None = Query(default=None, description="Filter by category"),
    min_price: float | None = Query(default=None, ge=0, description="Minimum price"),
    max_price: float | None = Query(default=None, ge=0, description="Maximum price"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
) -> SearchResponse:
    """
    Search products using semantic search with keyword fallback.

    - **q**: Search query (natural language supported)
    - **category_id**: Optional category filter
    - **min_price**: Optional minimum price filter
    - **max_price**: Optional maximum price filter
    - **page**: Page number
    - **page_size**: Results per page

    Returns products ranked by relevance with scores.
    """
    service = SearchService(db)
    skip = (page - 1) * page_size

    results, total = await service.search_products(
        q,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        skip=skip,
        limit=page_size,
    )

    pages = (total + page_size - 1) // page_size if total > 0 else 1

    search_results = [
        SearchResult(
            product=ProductResponse.model_validate(product),
            score=score,
        )
        for product, score in results
    ]

    # Determine best match
    best_match = None
    best_match_reason = None
    if search_results:
        best_match = search_results[0]
        if best_match.score > 0.8:
            best_match_reason = f"'{best_match.product.name}' is a strong match for your search."
        elif best_match.score > 0.5:
            best_match_reason = f"'{best_match.product.name}' may be what you're looking for."

    return SearchResponse(
        query=q,
        results=search_results,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        best_match=best_match,
        best_match_reason=best_match_reason,
    )


@router.get("/suggestions", response_model=SearchSuggestionsResponse)
async def get_search_suggestions(
    q: str = Query(..., min_length=1, max_length=100, description="Partial query"),
    limit: int = Query(default=5, ge=1, le=10, description="Max suggestions"),
    db: AsyncSession = Depends(get_db),
) -> SearchSuggestionsResponse:
    """
    Get search suggestions for autocomplete.

    - **q**: Partial search query
    - **limit**: Maximum number of suggestions

    Returns suggestions from product names and categories.
    """
    service = SearchService(db)
    suggestions_data = await service.get_search_suggestions(q, limit=limit)

    suggestions = [
        SearchSuggestion(
            text=s["text"],
            type=s["type"],
        )
        for s in suggestions_data
    ]

    return SearchSuggestionsResponse(
        suggestions=suggestions,
        recent_searches=[],  # TODO: Implement with session tracking
        popular_searches=[],  # TODO: Implement with analytics
    )


@router.get("/filters")
async def get_search_filters(
    category_id: int | None = Query(default=None, description="Category context"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get available search filters and facets.

    - **category_id**: Optional category to scope filters

    Returns available filters including price range and categories.
    """
    service = SearchService(db)
    facets = await service.get_filter_facets(category_id=category_id)

    return {
        "price_range": facets.get("price_range"),
        "categories": [
            {"id": c.id, "name": c.name, "slug": c.slug}
            for c in facets.get("categories", [])
        ],
    }
