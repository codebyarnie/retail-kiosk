"""Pydantic schemas for Session API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SessionCreate(BaseModel):
    """Schema for creating a new session."""

    device_type: Optional[str] = Field(None, max_length=50, description="Device type")


class SessionResponse(BaseModel):
    """Schema for session response."""

    model_config = ConfigDict(from_attributes=True)

    session_id: str
    device_type: Optional[str] = None
    created_at: datetime
    last_active_at: datetime
    expires_at: Optional[datetime] = None
