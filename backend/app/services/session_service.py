"""Session service for anonymous user session management."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserSession


class SessionService:
    """Service for session-related business logic."""

    # Session expires after 7 days of inactivity
    SESSION_TIMEOUT_DAYS = 7

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the session service."""
        self.db = db

    async def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session by session_id string."""
        result = await self.db.execute(
            select(UserSession).where(UserSession.session_id == session_id)
        )
        session = result.scalar_one_or_none()

        if session and session.is_expired():
            return None

        return session

    async def get_session_by_db_id(self, db_id: int) -> Optional[UserSession]:
        """Get session by database ID."""
        result = await self.db.execute(
            select(UserSession).where(UserSession.id == db_id)
        )
        return result.scalar_one_or_none()

    async def create_session(
        self,
        *,
        device_type: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> UserSession:
        """Create a new anonymous session."""
        expires_at = datetime.now(timezone.utc) + timedelta(days=self.SESSION_TIMEOUT_DAYS)

        session = UserSession(
            session_id=str(uuid.uuid4()),
            device_type=device_type,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=expires_at,
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_or_create_session(
        self,
        session_id: Optional[str] = None,
        *,
        device_type: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> UserSession:
        """
        Get existing session or create a new one.

        Args:
            session_id: Existing session ID to look up
            device_type: Device type for new session
            user_agent: User agent for new session
            ip_address: IP address for new session

        Returns:
            Existing or newly created session
        """
        if session_id:
            session = await self.get_session(session_id)
            if session:
                # Update last active timestamp
                await self.touch_session(session)
                return session

        # Create new session
        return await self.create_session(
            device_type=device_type,
            user_agent=user_agent,
            ip_address=ip_address,
        )

    async def touch_session(self, session: UserSession) -> None:
        """Update the last_active_at timestamp."""
        session.last_active_at = datetime.now(timezone.utc)
        session.expires_at = datetime.now(timezone.utc) + timedelta(
            days=self.SESSION_TIMEOUT_DAYS
        )
        await self.db.commit()

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        session = await self.get_session(session_id)
        if not session:
            return False

        await self.db.delete(session)
        await self.db.commit()
        return True

    async def cleanup_expired_sessions(self) -> int:
        """
        Delete expired sessions.

        Returns:
            Number of sessions deleted
        """
        from sqlalchemy import delete

        result = await self.db.execute(
            delete(UserSession).where(
                UserSession.expires_at < datetime.now(timezone.utc)
            )
        )
        await self.db.commit()
        return result.rowcount or 0
