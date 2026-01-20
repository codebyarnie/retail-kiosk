"""Analytics service for event tracking."""

from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AnalyticsEvent, EventType
from app.schemas.analytics import AnalyticsEventCreate


class AnalyticsService:
    """Service for analytics event tracking."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the analytics service."""
        self.db = db

    async def track_event(
        self,
        session_id: int,
        event_data: AnalyticsEventCreate,
    ) -> AnalyticsEvent:
        """Track a single analytics event."""
        event = AnalyticsEvent(
            session_id=session_id,
            event_type=event_data.event_type,
            event_data=event_data.event_data,
            product_sku=event_data.product_sku,
            search_query=event_data.search_query,
            event_timestamp=event_data.timestamp or datetime.now(timezone.utc),
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def track_events_batch(
        self,
        session_id: int,
        events: list[AnalyticsEventCreate],
    ) -> list[AnalyticsEvent]:
        """Track multiple analytics events at once."""
        created_events = []
        for event_data in events:
            event = AnalyticsEvent(
                session_id=session_id,
                event_type=event_data.event_type,
                event_data=event_data.event_data,
                product_sku=event_data.product_sku,
                search_query=event_data.search_query,
                event_timestamp=event_data.timestamp or datetime.now(timezone.utc),
            )
            self.db.add(event)
            created_events.append(event)

        await self.db.commit()
        return created_events

    async def get_session_events(
        self,
        session_id: int,
        *,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> list[AnalyticsEvent]:
        """Get events for a session."""
        query = (
            select(AnalyticsEvent)
            .where(AnalyticsEvent.session_id == session_id)
            .order_by(AnalyticsEvent.event_timestamp.desc())
            .limit(limit)
        )

        if event_type:
            query = query.where(AnalyticsEvent.event_type == event_type)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_session_summary(self, session_id: int) -> dict:
        """Get analytics summary for a session."""
        # Count events by type
        counts_query = (
            select(
                AnalyticsEvent.event_type,
                func.count(AnalyticsEvent.id),
            )
            .where(AnalyticsEvent.session_id == session_id)
            .group_by(AnalyticsEvent.event_type)
        )
        counts_result = await self.db.execute(counts_query)
        counts = dict(counts_result.all())

        # Get session duration
        time_query = (
            select(
                func.min(AnalyticsEvent.event_timestamp),
                func.max(AnalyticsEvent.event_timestamp),
            )
            .where(AnalyticsEvent.session_id == session_id)
        )
        time_result = await self.db.execute(time_query)
        first_event, last_event = time_result.one()

        duration_seconds = None
        if first_event and last_event:
            duration_seconds = int((last_event - first_event).total_seconds())

        return {
            "total_events": sum(counts.values()),
            "searches_performed": counts.get(EventType.SEARCH, 0),
            "products_viewed": counts.get(EventType.VIEW_PRODUCT, 0),
            "items_added_to_list": counts.get(EventType.ADD_TO_LIST, 0),
            "session_duration_seconds": duration_seconds,
        }

    async def get_popular_searches(
        self, period_hours: int = 24, limit: int = 10
    ) -> list[dict]:
        """Get popular search queries."""
        since = datetime.now(timezone.utc) - timedelta(hours=period_hours)

        query = (
            select(
                AnalyticsEvent.search_query,
                func.count(AnalyticsEvent.id).label("count"),
            )
            .where(
                AnalyticsEvent.event_type == EventType.SEARCH,
                AnalyticsEvent.event_timestamp >= since,
                AnalyticsEvent.search_query != None,
            )
            .group_by(AnalyticsEvent.search_query)
            .order_by(func.count(AnalyticsEvent.id).desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        return [{"query": row[0], "count": row[1]} for row in result.all()]

    async def get_top_viewed_products(
        self, period_hours: int = 24, limit: int = 10
    ) -> list[dict]:
        """Get most viewed products."""
        since = datetime.now(timezone.utc) - timedelta(hours=period_hours)

        query = (
            select(
                AnalyticsEvent.product_sku,
                func.count(AnalyticsEvent.id).label("view_count"),
            )
            .where(
                AnalyticsEvent.event_type == EventType.VIEW_PRODUCT,
                AnalyticsEvent.event_timestamp >= since,
                AnalyticsEvent.product_sku != None,
            )
            .group_by(AnalyticsEvent.product_sku)
            .order_by(func.count(AnalyticsEvent.id).desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        return [{"sku": row[0], "view_count": row[1]} for row in result.all()]

    async def cleanup_old_events(self, days: int = 90) -> int:
        """Delete events older than specified days."""
        from sqlalchemy import delete

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self.db.execute(
            delete(AnalyticsEvent).where(AnalyticsEvent.event_timestamp < cutoff)
        )
        await self.db.commit()
        return result.rowcount or 0
