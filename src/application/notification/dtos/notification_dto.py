"""Notification DTOs."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class NotificationDTO:
    """Notification data transfer object."""

    notification_id: str
    user_id: str
    notification_type: str
    status: str
    priority: str
    title: str
    message: str
    data: Dict[str, Any]
    sent_at: Optional[datetime]
    failed_at: Optional[datetime]
    error_message: Optional[str]
    retry_count: int
    created_at: datetime
    updated_at: datetime


@dataclass
class CreateNotificationDTO:
    """Create notification DTO."""

    user_id: str
    notification_type: str
    title: str
    message: str
    priority: str = "normal"
    data: Optional[Dict[str, Any]] = None


@dataclass
class SendNotificationDTO:
    """Send notification DTO."""

    notification_id: str
