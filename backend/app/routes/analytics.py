"""Analytics API routes."""

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.schemas.analytics import (
    AnalyticsBatchCreate,
    AnalyticsEventCreate,
    AnalyticsEventResponse,
    AnalyticsSummary,
    PopularSearchesResponse,
    TopProductsResponse,
)
from app.services.analytics_service import AnalyticsService
from app.services.session_service import SessionService

router = APIRouter(prefix="/analytics")


async def get_session_id(
    response: Response,
    session_id: str | None = Cookie(default=None, alias="session_id"),
    db: AsyncSession = Depends(get_db),
) -> int:
    """Get or create user session, returning the database ID."""
    session_service = SessionService(db)
    session = await session_service.get_or_create_session(session_id)

    if not session_id or session_id != session.session_id:
        response.set_cookie(
            key="session_id",
            value=session.session_id,
            max_age=7 * 24 * 60 * 60,
            httponly=True,
            samesite="lax",
        )

    return session.id


@router.post("/events", response_model=AnalyticsEventResponse, status_code=status.HTTP_201_CREATED)
async def track_event(
    event_data: AnalyticsEventCreate,
    response: Response,
    session_id: str | None = Cookie(default=None, alias="session_id"),
    db: AsyncSession = Depends(get_db),
) -> AnalyticsEventResponse:
    """
    Track a single analytics event.

    Event types include:
    - search: User performed a search
    - view_product: User viewed a product
    - add_to_list: User added product to list
    - remove_from_list: User removed product from list
    - page_view: User viewed a page
    """
    db_session_id = await get_session_id(response, session_id, db)
    service = AnalyticsService(db)
    event = await service.track_event(db_session_id, event_data)
    return AnalyticsEventResponse.model_validate(event)


@router.post("/events/batch", status_code=status.HTTP_201_CREATED)
async def track_events_batch(
    batch_data: AnalyticsBatchCreate,
    response: Response,
    session_id: str | None = Cookie(default=None, alias="session_id"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Track multiple analytics events at once.

    Useful for batching events from the frontend to reduce API calls.
    Maximum 100 events per batch.
    """
    db_session_id = await get_session_id(response, session_id, db)
    service = AnalyticsService(db)
    events = await service.track_events_batch(db_session_id, batch_data.events)
    return {"tracked": len(events)}


@router.get("/summary", response_model=AnalyticsSummary)
async def get_session_summary(
    response: Response,
    session_id: str | None = Cookie(default=None, alias="session_id"),
    db: AsyncSession = Depends(get_db),
) -> AnalyticsSummary:
    """Get analytics summary for the current session."""
    session_service = SessionService(db)
    session = await session_service.get_or_create_session(session_id)

    if not session_id or session_id != session.session_id:
        response.set_cookie(
            key="session_id",
            value=session.session_id,
            max_age=7 * 24 * 60 * 60,
            httponly=True,
            samesite="lax",
        )

    service = AnalyticsService(db)
    summary = await service.get_session_summary(session.id)

    return AnalyticsSummary(
        session_id=session.session_id,
        **summary,
    )


@router.get("/popular-searches", response_model=PopularSearchesResponse)
async def get_popular_searches(
    hours: int = Query(default=24, ge=1, le=720, description="Time period in hours"),
    limit: int = Query(default=10, ge=1, le=50, description="Max results"),
    db: AsyncSession = Depends(get_db),
) -> PopularSearchesResponse:
    """
    Get popular search queries.

    - **hours**: Time period to analyze (default: 24 hours)
    - **limit**: Maximum number of results
    """
    service = AnalyticsService(db)
    searches = await service.get_popular_searches(period_hours=hours, limit=limit)

    period = f"last_{hours}h" if hours < 24 else f"last_{hours // 24}d"
    return PopularSearchesResponse(searches=searches, period=period)


@router.get("/top-products", response_model=TopProductsResponse)
async def get_top_products(
    hours: int = Query(default=24, ge=1, le=720, description="Time period in hours"),
    limit: int = Query(default=10, ge=1, le=50, description="Max results"),
    db: AsyncSession = Depends(get_db),
) -> TopProductsResponse:
    """
    Get most viewed products.

    - **hours**: Time period to analyze (default: 24 hours)
    - **limit**: Maximum number of results
    """
    service = AnalyticsService(db)
    products = await service.get_top_viewed_products(period_hours=hours, limit=limit)

    period = f"last_{hours}h" if hours < 24 else f"last_{hours // 24}d"
    return TopProductsResponse(products=products, period=period)
