"""User Search Result entity."""

from dataclasses import dataclass

from src.domain.instagram_integration.value_objects.instagram_user_id import InstagramUserId
from src.domain.instagram_integration.value_objects.instagram_username import InstagramUsername
from src.domain.instagram_integration.value_objects.media_url import MediaUrl


@dataclass
class UserSearchResult:
    """User search result entity."""

    user_id: InstagramUserId
    username: InstagramUsername
    full_name: str
    profile_pic_url: MediaUrl
    is_verified: bool
    follower_count: int

    @classmethod
    def create(
        cls,
        user_id: InstagramUserId,
        username: InstagramUsername,
        full_name: str,
        profile_pic_url: MediaUrl,
        is_verified: bool,
        follower_count: int,
    ) -> "UserSearchResult":
        """Create user search result."""
        return cls(
            user_id=user_id,
            username=username,
            full_name=full_name,
            profile_pic_url=profile_pic_url,
            is_verified=is_verified,
            follower_count=follower_count,
        )
