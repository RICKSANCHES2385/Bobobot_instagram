"""Story Entity."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.shared.entities.base import BaseEntity
from ..value_objects.media_id import MediaId
from ..value_objects.media_url import MediaUrl
from ..value_objects.instagram_user_id import InstagramUserId


@dataclass(eq=False)
class Story(BaseEntity):
    """Instagram story entity."""
    
    media_id: MediaId = None
    user_id: InstagramUserId = None
    media_url: MediaUrl = None
    media_type: str = "IMAGE"  # IMAGE or VIDEO
    taken_at: datetime = None
    expires_at: Optional[datetime] = None
    
    @staticmethod
    def create(
        media_id: MediaId,
        user_id: InstagramUserId,
        media_url: MediaUrl,
        media_type: str = "IMAGE",
        taken_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None
    ) -> 'Story':
        """Create a new story.
        
        Args:
            media_id: Media ID
            user_id: User ID who posted the story
            media_url: Media URL
            media_type: Media type (IMAGE or VIDEO)
            taken_at: When story was posted
            expires_at: When story expires
            
        Returns:
            Story instance
        """
        if taken_at is None:
            taken_at = datetime.utcnow()
        
        return Story(
            id=media_id.value,
            media_id=media_id,
            user_id=user_id,
            media_url=media_url,
            media_type=media_type,
            taken_at=taken_at,
            expires_at=expires_at
        )
    
    def is_video(self) -> bool:
        """Check if story is a video."""
        return self.media_type == "VIDEO"
    
    def is_image(self) -> bool:
        """Check if story is an image."""
        return self.media_type == "IMAGE"
    
    def is_expired(self) -> bool:
        """Check if story is expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def __str__(self) -> str:
        """String representation."""
        return f"Story {self.media_id} ({self.media_type})"
