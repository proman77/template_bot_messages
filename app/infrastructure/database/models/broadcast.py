from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.infrastructure.database.models.broadcast_status import BroadcastStatus


class BroadcastCampaignModel(BaseModel):
    id: int = Field(..., description="Internal primary key")
    admin_id: int = Field(..., description="Telegram ID of the admin who created the campaign")
    status: BroadcastStatus = Field(..., description="Current status of the campaign")
    created_at: datetime = Field(..., description="Timestamp of creation")
    updated_at: datetime = Field(..., description="Timestamp of last update")
    scheduled_at: datetime | None = Field(None, description="Optional scheduled time for the broadcast")

    class Config:
        from_attributes = True


class BroadcastMessageModel(BaseModel):
    id: int = Field(..., description="Internal primary key")
    campaign_id: int = Field(..., description="Reference to the campaign")
    language_code: str = Field(..., description="Language code (e.g., 'ru', 'en') or 'all'")
    content_type: str = Field(..., description="Type of content (text, photo, etc.)")
    file_id: str | None = Field(None, description="Telegram file_id for media")
    text: str | None = Field(None, description="Message text")
    caption: str | None = Field(None, description="Caption for media")
    reply_markup: dict[str, Any] | None = Field(None, description="Inline keyboard stored as JSON")

    class Config:
        from_attributes = True
