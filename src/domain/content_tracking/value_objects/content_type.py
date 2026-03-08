"""Content Type Value Object."""

from dataclasses import dataclass
from enum import Enum

from src.domain.shared.value_objects.base import BaseValueObject


class ContentTypeEnum(str, Enum):
    """Content type enumeration."""

    STORIES = "stories"
    POSTS = "posts"
    REELS = "reels"
    ALL = "all"


@dataclass(frozen=True)
class ContentType(BaseValueObject):
    """Content type value object."""

    value: ContentTypeEnum

    def __post_init__(self):
        """Validate content type."""
        if not isinstance(self.value, ContentTypeEnum):
            raise ValueError(f"Invalid content type: {self.value}")

    def is_stories(self) -> bool:
        """Check if tracking stories."""
        return self.value == ContentTypeEnum.STORIES

    def is_posts(self) -> bool:
        """Check if tracking posts."""
        return self.value == ContentTypeEnum.POSTS

    def is_reels(self) -> bool:
        """Check if tracking reels."""
        return self.value == ContentTypeEnum.REELS

    def is_all(self) -> bool:
        """Check if tracking all content."""
        return self.value == ContentTypeEnum.ALL

    def __str__(self) -> str:
        """String representation."""
        return self.value.value
