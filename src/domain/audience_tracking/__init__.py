"""Audience Tracking Domain."""

from .aggregates.audience_tracking import AudienceTracking
from .value_objects.tracking_id import TrackingId
from .value_objects.follower_count import FollowerCount
from .value_objects.following_count import FollowingCount
from .value_objects.tracking_price import TrackingPrice
from .repositories.audience_tracking_repository import AudienceTrackingRepository
from .exceptions import (
    AudienceTrackingException,
    TrackingNotFoundException,
    FollowerLimitExceededException,
    DuplicateTrackingException,
    InactiveSubscriptionException,
    ExpiredSubscriptionException,
)

__all__ = [
    # Aggregates
    "AudienceTracking",
    # Value Objects
    "TrackingId",
    "FollowerCount",
    "FollowingCount",
    "TrackingPrice",
    # Repositories
    "AudienceTrackingRepository",
    # Exceptions
    "AudienceTrackingException",
    "TrackingNotFoundException",
    "FollowerLimitExceededException",
    "DuplicateTrackingException",
    "InactiveSubscriptionException",
    "ExpiredSubscriptionException",
]
