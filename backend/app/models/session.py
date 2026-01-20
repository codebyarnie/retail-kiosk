"""User session model for anonymous session management."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .analytics import AnalyticsEvent
    from .list import UserList


class UserSession(Base, TimestampMixin):
    """
    User session model for anonymous session-based access.

    Sessions are created automatically for kiosk users without requiring
    login. They track user activity and link to shopping lists.
    """

    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid.uuid4()),
    )

    # Session metadata
    device_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    # Session activity tracking
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    lists: Mapped[list["UserList"]] = relationship(
        "UserList", back_populates="session", cascade="all, delete-orphan"
    )
    analytics_events: Mapped[list["AnalyticsEvent"]] = relationship(
        "AnalyticsEvent", back_populates="session", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<UserSession(id={self.id}, session_id='{self.session_id[:8]}...')>"

    def is_expired(self) -> bool:
        """Check if the session has expired."""
        if self.expires_at is None:
            return False
        return datetime.now(self.expires_at.tzinfo) > self.expires_at

    def touch(self) -> None:
        """Update the last_active_at timestamp."""
        self.last_active_at = datetime.now(self.last_active_at.tzinfo)
