"""Content Tracking DTOs."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TrackingDTO:
    """Tracking data transfer object."""

    tracking_id: str
    user_id: str
    instagram_user_id: str
    instagram_username: str
    content_type: str
    status: str
    check_interval_minutes: int
    notification_enabled: bool
    last_check_at: Optional[datetime]
    last_content_id: Optional[str]
    created_at: datetime
    updated_at: datetime


@dataclass
class StartTrackingCommand:
    """Command to start tracking."""

    user_id: str
    instagram_username: str
    content_type: str  # "stories", "posts", "reels", "all"
    check_interval_minutes: int = 30
    notification_enabled: bool = True


@dataclass
class ContentUpdateDTO:
    """Content update data transfer object."""

    tracking_id: str
    instagram_username: str
    content_type: str
    content_id: str
    content_url: str
    detected_at: datetime


@dataclass
class UserTrackingsDTO:
    """User trackings data transfer object."""

    user_id: str
    trackings: list[TrackingDTO]
    total_count: int
    active_count: int
