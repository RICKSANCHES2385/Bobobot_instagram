"""Reel Entity."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.shared.entities.base import BaseEntity
from ..value_objects.media_id import MediaId
from ..value_objects.media_url import MediaUrl
from ..value_objects.caption import Caption
from ..value_objects.instagram_user_id import InstagramUserId


@dataclass(eq=False)
class Reel(BaseEntity):
    """Instagram reel entity."""
    
    media_id: MediaId = None
    user_id: InstagramUserId = None
    video_url: MediaUrl = None
    thumbnail_url: Optional[MediaUrl] = None
    caption: Caption = None
    like_count: int = 0
    comment_count: int = 0
    play_count: int = 0
    taken_at: datetime = None
    
    @staticmethod
    def create(
        media_id: MediaId,
        user_id: InstagramUserId,
        video_url: MediaUrl,
        caption: Caption,
        thumbnail_url: Optional[MediaUrl] = None,
        like_count: int = 0,
        comment_count: int = 0,
        play_count: int = 0,
        taken_at: Optional[datetime] = None
    ) -> 'Reel':
        """Create a new reel.
        
        Args:
            media_id: Media ID
            user_id: User ID who posted
            video_url: Video URL
            caption: Reel caption
            thumbnail_url: Thumbnail URL
            like_count: Number of likes
            comment_count: Number of comments
            play_count: Number of plays
            taken_at: When reel was created
            
        Returns:
            Reel instance
        """
        if taken_at is None:
            taken_at = datetime.utcnow()
        
        return Reel(
            id=media_id.value,
            media_id=media_id,
            user_id=user_id,
            video_url=video_url,
            thumbnail_url=thumbnail_url,
            caption=caption,
            like_count=like_count,
            comment_count=comment_count,
            play_count=play_count,
            taken_at=taken_at
        )
    
    def has_thumbnail(self) -> bool:
        """Check if reel has a thumbnail."""
        return self.thumbnail_url is not None
    
    def has_likes(self) -> bool:
        """Check if reel has likes."""
        return self.like_count > 0
    
    def has_comments(self) -> bool:
        """Check if reel has comments."""
        return self.comment_count > 0
    
    def has_plays(self) -> bool:
        """Check if reel has plays."""
        return self.play_count > 0
    
    def __str__(self) -> str:
        """String representation."""
        return f"Reel {self.media_id}"
