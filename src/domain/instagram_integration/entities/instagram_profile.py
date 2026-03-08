"""Instagram Profile Entity."""
from dataclasses import dataclass
from typing import Optional

from src.domain.shared.entities.base import BaseEntity
from ..value_objects.instagram_username import InstagramUsername
from ..value_objects.instagram_user_id import InstagramUserId
from ..value_objects.bio import Bio
from ..value_objects.profile_statistics import ProfileStatistics
from ..value_objects.media_url import MediaUrl


@dataclass(eq=False)
class InstagramProfile(BaseEntity):
    """Instagram profile entity."""
    
    username: InstagramUsername = None
    user_id: InstagramUserId = None
    full_name: str = ""
    bio: Bio = None
    statistics: ProfileStatistics = None
    is_private: bool = False
    is_verified: bool = False
    profile_pic_url: Optional[MediaUrl] = None
    external_url: Optional[str] = None
    
    @staticmethod
    def create(
        username: InstagramUsername,
        user_id: InstagramUserId,
        full_name: str,
        bio: Bio,
        statistics: ProfileStatistics,
        is_private: bool = False,
        is_verified: bool = False,
        profile_pic_url: Optional[MediaUrl] = None,
        external_url: Optional[str] = None
    ) -> 'InstagramProfile':
        """Create a new Instagram profile.
        
        Args:
            username: Instagram username
            user_id: Instagram user ID
            full_name: Full name
            bio: Biography
            statistics: Profile statistics
            is_private: Whether profile is private
            is_verified: Whether profile is verified
            profile_pic_url: Profile picture URL
            external_url: External URL
            
        Returns:
            InstagramProfile instance
        """
        return InstagramProfile(
            id=user_id.value,  # Use user_id as entity id
            username=username,
            user_id=user_id,
            full_name=full_name,
            bio=bio,
            statistics=statistics,
            is_private=is_private,
            is_verified=is_verified,
            profile_pic_url=profile_pic_url,
            external_url=external_url
        )
    
    def has_profile_picture(self) -> bool:
        """Check if profile has a profile picture."""
        return self.profile_pic_url is not None
    
    def has_external_url(self) -> bool:
        """Check if profile has an external URL."""
        return self.external_url is not None and self.external_url.strip() != ""
    
    def __str__(self) -> str:
        """String representation."""
        return f"@{self.username} ({self.full_name})"
