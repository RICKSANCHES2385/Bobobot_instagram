"""Content Tracking Aggregate."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from src.domain.shared.entities.base import AggregateRoot
from src.domain.content_tracking.value_objects.tracking_id import TrackingId
from src.domain.content_tracking.value_objects.tracking_status import TrackingStatus, TrackingStatusEnum
from src.domain.content_tracking.value_objects.content_type import ContentType, ContentTypeEnum
from src.domain.content_tracking.value_objects.check_interval import CheckInterval
from src.domain.instagram_integration.value_objects.instagram_user_id import InstagramUserId
from src.domain.instagram_integration.value_objects.instagram_username import InstagramUsername
from src.domain.content_tracking.events.tracking_events import (
    TrackingStartedEvent,
    TrackingPausedEvent,
    TrackingResumedEvent,
    TrackingStoppedEvent,
    ContentUpdateDetectedEvent,
)


@dataclass(eq=False)
class ContentTracking(AggregateRoot):
    """Content tracking aggregate root."""

    tracking_id: TrackingId = None
    user_id: str = None  # Telegram user ID
    instagram_user_id: InstagramUserId = None
    instagram_username: InstagramUsername = None
    content_type: ContentType = None
    status: TrackingStatus = None
    check_interval: CheckInterval = None
    last_check_at: Optional[datetime] = None
    last_content_id: Optional[str] = None
    notification_enabled: bool = True

    @staticmethod
    def create(
        tracking_id: TrackingId,
        user_id: str,
        instagram_user_id: InstagramUserId,
        instagram_username: InstagramUsername,
        content_type: ContentType,
        check_interval: CheckInterval,
        notification_enabled: bool = True,
    ) -> "ContentTracking":
        """Create new content tracking.
        
        Args:
            tracking_id: Tracking ID
            user_id: Telegram user ID
            instagram_user_id: Instagram user ID
            instagram_username: Instagram username
            content_type: Content type to track
            check_interval: Check interval
            notification_enabled: Whether notifications are enabled
            
        Returns:
            ContentTracking instance
        """
        tracking = ContentTracking(
            id=tracking_id.value,
            tracking_id=tracking_id,
            user_id=user_id,
            instagram_user_id=instagram_user_id,
            instagram_username=instagram_username,
            content_type=content_type,
            status=TrackingStatus(TrackingStatusEnum.ACTIVE),
            check_interval=check_interval,
            notification_enabled=notification_enabled,
        )

        # Add domain event
        tracking.add_domain_event(
            TrackingStartedEvent(
                tracking_id=tracking_id.value,
                user_id=user_id,
                instagram_username=instagram_username.value,
                content_type=content_type.value.value,
            )
        )

        return tracking

    def pause(self) -> None:
        """Pause tracking."""
        if not self.status.is_active():
            raise ValueError("Can only pause active tracking")

        self.status = TrackingStatus(TrackingStatusEnum.PAUSED)
        self._touch()

        self.add_domain_event(
            TrackingPausedEvent(
                tracking_id=self.tracking_id.value,
                user_id=self.user_id,
            )
        )

    def resume(self) -> None:
        """Resume tracking."""
        if not self.status.is_paused():
            raise ValueError("Can only resume paused tracking")

        self.status = TrackingStatus(TrackingStatusEnum.ACTIVE)
        self._touch()

        self.add_domain_event(
            TrackingResumedEvent(
                tracking_id=self.tracking_id.value,
                user_id=self.user_id,
            )
        )

    def stop(self) -> None:
        """Stop tracking."""
        if self.status.is_stopped():
            raise ValueError("Tracking is already stopped")

        self.status = TrackingStatus(TrackingStatusEnum.STOPPED)
        self._touch()

        self.add_domain_event(
            TrackingStoppedEvent(
                tracking_id=self.tracking_id.value,
                user_id=self.user_id,
            )
        )

    def update_last_check(self, content_id: Optional[str] = None) -> None:
        """Update last check timestamp.
        
        Args:
            content_id: Latest content ID (optional)
        """
        self.last_check_at = datetime.utcnow()
        if content_id:
            self.last_content_id = content_id
        self._touch()

    def detect_new_content(self, content_id: str, content_url: str) -> None:
        """Detect new content.
        
        Args:
            content_id: New content ID
            content_url: Content URL
        """
        if not self.status.is_active():
            return

        # Update last content ID
        self.last_content_id = content_id
        self.last_check_at = datetime.utcnow()
        self._touch()

        # Add domain event
        if self.notification_enabled:
            self.add_domain_event(
                ContentUpdateDetectedEvent(
                    tracking_id=self.tracking_id.value,
                    user_id=self.user_id,
                    instagram_username=self.instagram_username.value,
                    content_type=self.content_type.value.value,
                    content_id=content_id,
                    content_url=content_url,
                )
            )

    def update_check_interval(self, new_interval: CheckInterval) -> None:
        """Update check interval.
        
        Args:
            new_interval: New check interval
        """
        self.check_interval = new_interval
        self._touch()

    def enable_notifications(self) -> None:
        """Enable notifications."""
        self.notification_enabled = True
        self._touch()

    def disable_notifications(self) -> None:
        """Disable notifications."""
        self.notification_enabled = False
        self._touch()

    def should_check_now(self) -> bool:
        """Check if tracking should be checked now."""
        if not self.status.is_active():
            return False

        if self.last_check_at is None:
            return True

        time_since_last_check = datetime.utcnow() - self.last_check_at
        return time_since_last_check.total_seconds() >= self.check_interval.to_seconds()

    def __str__(self) -> str:
        """String representation."""
        return f"Tracking @{self.instagram_username} ({self.content_type}) - {self.status}"
