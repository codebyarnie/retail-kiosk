"""Analytics event model for tracking user behavior."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .session import UserSession


class EventType(str, Enum):
    """Types of analytics events that can be tracked."""

    # Search events
    SEARCH = "search"
    SEARCH_NO_RESULTS = "search_no_results"

    # Product events
    VIEW_PRODUCT = "view_product"
    VIEW_CATEGORY = "view_category"

    # List events
    ADD_TO_LIST = "add_to_list"
    REMOVE_FROM_LIST = "remove_from_list"
    UPDATE_QUANTITY = "update_quantity"

    # Session events
    SESSION_START = "session_start"
    SESSION_END = "session_end"

    # QR events
    QR_GENERATED = "qr_generated"
    QR_SCANNED = "qr_scanned"
    LIST_SYNCED = "list_synced"

    # UI events
    PAGE_VIEW = "page_view"
    FILTER_APPLIED = "filter_applied"


class AnalyticsEvent(Base):
    """
    Analytics event model for tracking user behavior.

    Events are stored with flexible JSONB data to capture different
    event types with varying attributes.
    """

    __tablename__ = "analytics_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_sessions.id", ondelete="CASCADE"), nullable=False
    )

    # Event identification
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    event_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Event data (flexible structure per event type)
    # Examples:
    # - search: {"query": "deck screws", "results_count": 15, "filters": {...}}
    # - view_product: {"sku": "ABC123", "source": "search", "position": 3}
    # - add_to_list: {"sku": "ABC123", "quantity": 2, "list_id": "..."}
    event_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, default=dict)

    # Optional references for quick querying
    product_sku: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    search_query: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationship
    session: Mapped["UserSession"] = relationship(
        "UserSession", back_populates="analytics_events"
    )

    __table_args__ = (
        Index("ix_analytics_session_type", "session_id", "event_type"),
        Index("ix_analytics_timestamp_type", "event_timestamp", "event_type"),
    )

    def __repr__(self) -> str:
        return f"<AnalyticsEvent(type='{self.event_type}', session={self.session_id})>"
