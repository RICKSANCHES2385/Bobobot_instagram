"""Highlight Entity."""
from dataclasses import dataclass
from typing import List

from src.domain.shared.entities.base import BaseEntity
from ..value_objects.highlight_id import HighlightId
from ..value_objects.highlight_title import HighlightTitle
from ..value_objects.media_url import MediaUrl
from ..value_objects.instagram_user_id import InstagramUserId


@dataclass(eq=False)
class Highlight(BaseEntity):
    """Instagram highlight entity."""
    
    highlight_id: HighlightId = None
    user_id: InstagramUserId = None
    title: HighlightTitle = None
    cover_url: MediaUrl = None
    story_count: int = 0
    
    @staticmethod
    def create(
        highlight_id: HighlightId,
        user_id: InstagramUserId,
        title: HighlightTitle,
        cover_url: MediaUrl,
        story_count: int = 0
    ) -> 'Highlight':
        """Create a new highlight.
        
        Args:
            highlight_id: Highlight ID
            user_id: User ID who owns the highlight
            title: Highlight title
            cover_url: Cover image URL
            story_count: Number of stories in highlight
            
        Returns:
            Highlight instance
        """
        return Highlight(
            id=highlight_id.value,
            highlight_id=highlight_id,
            user_id=user_id,
            title=title,
            cover_url=cover_url,
            story_count=story_count
        )
    
    def has_stories(self) -> bool:
        """Check if highlight has stories."""
        return self.story_count > 0
    
    def __str__(self) -> str:
        """String representation."""
        return f"Highlight '{self.title}' ({self.story_count} stories)"
