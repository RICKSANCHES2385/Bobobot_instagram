"""Audience Tracking Domain Exceptions."""


class AudienceTrackingException(Exception):
    """Base exception for audience tracking domain."""

    pass


class TrackingNotFoundException(AudienceTrackingException):
    """Raised when tracking subscription is not found."""

    def __init__(self, tracking_id: int):
        """Initialize exception.
        
        Args:
            tracking_id: Tracking ID that was not found
        """
        super().__init__(f"Audience tracking subscription {tracking_id} not found")
        self.tracking_id = tracking_id


class FollowerLimitExceededException(AudienceTrackingException):
    """Raised when target account exceeds follower limit."""

    def __init__(self, username: str, follower_count: int, limit: int = 100_000):
        """Initialize exception.
        
        Args:
            username: Instagram username
            follower_count: Current follower count
            limit: Maximum allowed followers
        """
        super().__init__(
            f"Account @{username} has {follower_count:,} followers, "
            f"which exceeds the limit of {limit:,}"
        )
        self.username = username
        self.follower_count = follower_count
        self.limit = limit


class DuplicateTrackingException(AudienceTrackingException):
    """Raised when trying to create duplicate tracking subscription."""

    def __init__(self, user_id: int, target_username: str):
        """Initialize exception.
        
        Args:
            user_id: User ID
            target_username: Target Instagram username
        """
        super().__init__(
            f"User {user_id} already has an active tracking subscription for @{target_username}"
        )
        self.user_id = user_id
        self.target_username = target_username


class InactiveSubscriptionException(AudienceTrackingException):
    """Raised when trying to use inactive subscription."""

    def __init__(self, tracking_id: int):
        """Initialize exception.
        
        Args:
            tracking_id: Tracking ID
        """
        super().__init__(f"Tracking subscription {tracking_id} is inactive")
        self.tracking_id = tracking_id


class ExpiredSubscriptionException(AudienceTrackingException):
    """Raised when trying to use expired subscription."""

    def __init__(self, tracking_id: int):
        """Initialize exception.
        
        Args:
            tracking_id: Tracking ID
        """
        super().__init__(f"Tracking subscription {tracking_id} has expired")
        self.tracking_id = tracking_id
