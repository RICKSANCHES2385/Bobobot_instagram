"""Use case for getting user's request history."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from ....domain.instagram_integration.entities.instagram_request import InstagramRequest
from ....domain.instagram_integration.repositories.instagram_request_repository import (
    InstagramRequestRepository
)
from ....domain.instagram_integration.value_objects.request_type import RequestType
from ....infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass
class GetUserRequestHistoryQuery:
    """Query for getting user's request history."""
    
    user_id: str
    request_type: Optional[RequestType] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 100
    offset: int = 0


@dataclass
class UserRequestHistoryDTO:
    """DTO for user request history."""
    
    requests: List[InstagramRequest]
    total_count: int
    success_count: int
    failed_count: int


class GetUserRequestHistoryUseCase:
    """Use case for getting user's request history."""
    
    def __init__(self, request_repository: InstagramRequestRepository):
        """Initialize use case."""
        self.request_repository = request_repository
    
    async def execute(
        self,
        query: GetUserRequestHistoryQuery
    ) -> UserRequestHistoryDTO:
        """Execute use case."""
        try:
            # Get requests based on filters
            if query.request_type:
                requests = await self.request_repository.get_user_requests_by_type(
                    user_id=query.user_id,
                    request_type=query.request_type,
                    limit=query.limit
                )
            elif query.start_date and query.end_date:
                requests = await self.request_repository.get_user_requests_by_date_range(
                    user_id=query.user_id,
                    start_date=query.start_date,
                    end_date=query.end_date
                )
            else:
                requests = await self.request_repository.get_user_requests(
                    user_id=query.user_id,
                    limit=query.limit,
                    offset=query.offset
                )
            
            # Calculate statistics
            total_count = len(requests)
            success_count = sum(1 for r in requests if r.is_successful())
            failed_count = sum(1 for r in requests if r.is_failed())
            
            logger.info(
                f"Retrieved request history for user {query.user_id}: "
                f"{total_count} requests"
            )
            
            return UserRequestHistoryDTO(
                requests=requests,
                total_count=total_count,
                success_count=success_count,
                failed_count=failed_count
            )
            
        except Exception as e:
            logger.error(f"Error getting user request history: {e}")
            raise
