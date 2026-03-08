"""Comment Entity."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.shared.entities.base import BaseEntity
from ..value_objects.comment_id import CommentId
from ..value_objects.comment_text import CommentText
from ..value_objects.instagram_user_id import InstagramUserId
from ..value_objects.instagram_username import InstagramUsername
from ..value_objects.media_id import MediaId


@dataclass(eq=False)
class Comment(BaseEntity):
    """Instagram comment entity."""
    
    comment_id: CommentId = None
    media_id: MediaId = None
    user_id: InstagramUserId = None
    username: InstagramUsername = None
    text: CommentText = None
    like_count: int = 0
    created_at: datetime = None
    
    @staticmethod
    def create(
        comment_id: CommentId,
        media_id: MediaId,
        user_id: InstagramUserId,
        username: InstagramUsername,
        text: CommentText,
        like_count: int = 0,
        created_at: Optional[datetime] = None
    ) -> 'Comment':
        """Create a new comment.
        
        Args:
            comment_id: Comment ID
            media_id: Media ID the comment belongs to
            user_id: User ID who posted the comment
            username: Username who posted the comment
            text: Comment text
            like_count: Number of likes
            created_at: When comment was created
            
        Returns:
            Comment instance
        """
        if created_at is None:
            created_at = datetime.utcnow()
        
        return Comment(
            id=comment_id.value,
            comment_id=comment_id,
            media_id=media_id,
            user_id=user_id,
            username=username,
            text=text,
            like_count=like_count,
            created_at=created_at
        )
    
    def has_likes(self) -> bool:
        """Check if comment has likes."""
        return self.like_count > 0
    
    def __str__(self) -> str:
        """String representation."""
        return f"Comment by @{self.username}: {self.text.truncate(50)}"
