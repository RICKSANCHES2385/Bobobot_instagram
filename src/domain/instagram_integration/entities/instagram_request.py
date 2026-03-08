"""Instagram Request entity for logging API requests."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ...shared.entities.base import Entity
from ..value_objects.request_type import RequestType
from ..value_objects.request_status import RequestStatus


@dataclass(eq=False)
class InstagramRequest(Entity):
    """Instagram API request entity for analytics."""
    
    user_id: str  # Telegram user ID
    request_type: RequestType
    target_username: str
    status: RequestStatus
    error_message: Optional[str] = None
    response_time_ms: Optional[int] = None
    created_at: datetime = None
    
    def __post_init__(self):
        """Initialize created_at if not provided."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    @staticmethod
    def create(
        user_id: str,
        request_type: RequestType,
        target_username: str,
        status: RequestStatus,
        error_message: Optional[str] = None,
        response_time_ms: Optional[int] = None,
    ) -> "InstagramRequest":
        """Create new Instagram request log entry."""
        return InstagramRequest(
            id=None,  # Will be set by repository
            user_id=user_id,
            request_type=request_type,
            target_username=target_username,
            status=status,
            error_message=error_message,
            response_time_ms=response_time_ms,
            created_at=datetime.utcnow(),
        )
    
    def is_successful(self) -> bool:
        """Check if request was successful."""
        return self.status.is_success()
    
    def is_failed(self) -> bool:
        """Check if request failed."""
        return self.status.is_failed()
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"Request {self.request_type.value} "
            f"for @{self.target_username} - {self.status.value}"
        )
