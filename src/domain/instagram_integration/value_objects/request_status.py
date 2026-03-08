"""Request status value object."""

from dataclasses import dataclass
from enum import Enum

from ...shared.value_objects.base import BaseValueObject


class RequestStatusEnum(str, Enum):
    """Request status enumeration."""
    
    SUCCESS = "success"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"
    UNAUTHORIZED = "unauthorized"
    NOT_FOUND = "not_found"


@dataclass(frozen=True)
class RequestStatus(BaseValueObject):
    """Request status value object."""
    
    value: RequestStatusEnum
    
    @staticmethod
    def success() -> 'RequestStatus':
        """Create success status."""
        return RequestStatus(value=RequestStatusEnum.SUCCESS)
    
    @staticmethod
    def failed() -> 'RequestStatus':
        """Create failed status."""
        return RequestStatus(value=RequestStatusEnum.FAILED)
    
    @staticmethod
    def rate_limited() -> 'RequestStatus':
        """Create rate limited status."""
        return RequestStatus(value=RequestStatusEnum.RATE_LIMITED)
    
    @staticmethod
    def unauthorized() -> 'RequestStatus':
        """Create unauthorized status."""
        return RequestStatus(value=RequestStatusEnum.UNAUTHORIZED)
    
    @staticmethod
    def not_found() -> 'RequestStatus':
        """Create not found status."""
        return RequestStatus(value=RequestStatusEnum.NOT_FOUND)
    
    def is_success(self) -> bool:
        """Check if status is success."""
        return self.value == RequestStatusEnum.SUCCESS
    
    def is_failed(self) -> bool:
        """Check if status is failed."""
        return self.value in [
            RequestStatusEnum.FAILED,
            RequestStatusEnum.RATE_LIMITED,
            RequestStatusEnum.UNAUTHORIZED,
            RequestStatusEnum.NOT_FOUND,
        ]
