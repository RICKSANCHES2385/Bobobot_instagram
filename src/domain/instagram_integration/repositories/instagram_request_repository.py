"""Instagram Request repository interface."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from ..entities.instagram_request import InstagramRequest
from ..value_objects.request_type import RequestType
from ..value_objects.request_status import RequestStatus


class InstagramRequestRepository(ABC):
    """Repository interface for Instagram requests."""
    
    @abstractmethod
    async def save(self, request: InstagramRequest) -> InstagramRequest:
        """Save Instagram request."""
        pass
    
    @abstractmethod
    async def get_by_id(self, request_id: str) -> Optional[InstagramRequest]:
        """Get request by ID."""
        pass
    
    @abstractmethod
    async def get_user_requests(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[InstagramRequest]:
        """Get user's request history."""
        pass
    
    @abstractmethod
    async def get_user_requests_by_type(
        self,
        user_id: str,
        request_type: RequestType,
        limit: int = 100
    ) -> List[InstagramRequest]:
        """Get user's requests by type."""
        pass
    
    @abstractmethod
    async def get_user_requests_by_date_range(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[InstagramRequest]:
        """Get user's requests within date range."""
        pass
    
    @abstractmethod
    async def count_user_requests_today(self, user_id: str) -> int:
        """Count user's requests today."""
        pass
    
    @abstractmethod
    async def count_failed_requests(
        self,
        user_id: str,
        since: datetime
    ) -> int:
        """Count failed requests since given time."""
        pass
    
    @abstractmethod
    async def get_recent_requests(
        self,
        limit: int = 100
    ) -> List[InstagramRequest]:
        """Get recent requests (for admin/analytics)."""
        pass
