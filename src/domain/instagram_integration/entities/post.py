"""Post Entity."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from src.domain.shared.entities.base import BaseEntity
from ..value_objects.media_id import MediaId
from ..value_objects.media_url import MediaUrl
from ..value_objects.caption import Caption
from ..value_objects.instagram_user_id import InstagramUserId


@dataclass(eq=False)
class Post(BaseEntity):
    """Instagram post entity."""
    
    media_id: MediaId = None
    user_id: InstagramUserId = None
    media_urls: List[MediaUrl] = None
    caption: Caption = None
    media_type: str = "IMAGE"  # IMAGE, VIDEO, or CAROUSEL
    like_count: int = 0
    comment_count: int = 0
    taken_at: datetime = None
    
    @staticmethod
    def create(
        media_id: MediaId,
        user_id: InstagramUserId,
        media_urls: List[MediaUrl],
        caption: Caption,
        media_type: str = "IMAGE",
        like_count: int = 0,
        comment_count: int = 0,
        taken_at: Optional[datetime] = None
    ) -> 'Post':
        """Create a new post.
        
        Args:
            media_id: Media ID
            user_id: User ID who posted
            media_urls: List of media URLs
            caption: Post caption
            media_type: Media type (IMAGE, VIDEO, or CAROUSEL)
            like_count: Number of likes
            comment_count: Number of comments
            taken_at: When post was created
            
        Returns:
            Post instance
        """
        if taken_at is None:
            taken_at = datetime.utcnow()
        
        if media_urls is None:
            media_urls = []
        
        return Post(
            id=media_id.value,
            media_id=media_id,
            user_id=user_id,
            media_urls=media_urls,
            caption=caption,
            media_type=media_type,
            like_count=like_count,
            comment_count=comment_count,
            taken_at=taken_at
        )
    
    def is_video(self) -> bool:
        """Check if post is a video."""
        return self.media_type == "VIDEO"
    
    def is_image(self) -> bool:
        """Check if post is an image."""
        return self.media_type == "IMAGE"
    
    def is_carousel(self) -> bool:
        """Check if post is a carousel."""
        return self.media_type == "CAROUSEL"
    
    def has_multiple_media(self) -> bool:
        """Check if post has multiple media items."""
        return len(self.media_urls) > 1
    
    def has_likes(self) -> bool:
        """Check if post has likes."""
        return self.like_count > 0
    
    def has_comments(self) -> bool:
        """Check if post has comments."""
        return self.comment_count > 0
    
    def __str__(self) -> str:
        """String representation."""
        return f"Post {self.media_id} ({self.media_type})"
