"""Use case for logging Instagram API requests."""

from dataclasses import dataclass
from typing import Optional

from ....domain.instagram_integration.entities.instagram_request import InstagramRequest
from ....domain.instagram_integration.repositories.instagram_request_repository import (
    InstagramRequestRepository
)
from ....domain.instagram_integration.value_objects.request_type import RequestType
from ....domain.instagram_integration.value_objects.request_status import RequestStatus
from ....infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass
class LogInstagramRequestCommand:
    """Command for logging Instagram request."""
    
    user_id: str
    request_type: RequestType
    target_username: str
    status: RequestStatus
    error_message: Optional[str] = None
    response_time_ms: Optional[int] = None


class LogInstagramRequestUseCase:
    """Use case for logging Instagram API requests."""
    
    def __init__(self, request_repository: InstagramRequestRepository):
        """Initialize use case."""
        self.request_repository = request_repository
    
    async def execute(self, command: LogInstagramRequestCommand) -> InstagramRequest:
        """Execute use case."""
        try:
            # Create request entity
            request = InstagramRequest.create(
                user_id=command.user_id,
                request_type=command.request_type,
                target_username=command.target_username,
                status=command.status,
                error_message=command.error_message,
                response_time_ms=command.response_time_ms,
            )
            
            # Save to repository
            saved_request = await self.request_repository.save(request)
            
            logger.info(
                f"Logged Instagram request: user={command.user_id}, "
                f"type={command.request_type.value.value}, "
                f"status={command.status.value.value}"
            )
            
            return saved_request
            
        except Exception as e:
            logger.error(f"Error logging Instagram request: {e}")
            raise
