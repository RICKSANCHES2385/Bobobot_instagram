"""Content Type Value Object."""
from dataclasses import dataclass
from enum import Enum

from src.domain.shared.value_objects.base import BaseValueObject


class ContentTypeEnum(str, Enum):
    """Content type enumeration."""
    
    STORY = "STORY"
    POST = "POST"
    REEL = "REEL"
    HIGHLIGHT = "HIGHLIGHT"
    TAGGED_POST = "TAGGED_POST"


@dataclass(frozen=True)
class ContentType(BaseValueObject):
    """Content type value object."""
    
    value: ContentTypeEnum
    
    def __post_init__(self):
        """Validate content type."""
        if not isinstance(self.value, ContentTypeEnum):
            if isinstance(self.value, str):
                try:
                    object.__setattr__(self, "value", ContentTypeEnum(self.value))
                except ValueError:
                    raise ValueError(f"Invalid content type: {self.value}")
            else:
                raise ValueError(f"Content type must be ContentTypeEnum or str, got {type(self.value)}")
    
    @staticmethod
    def story() -> 'ContentType':
        """Create story content type."""
        return ContentType(value=ContentTypeEnum.STORY)
    
    @staticmethod
    def post() -> 'ContentType':
        """Create post content type."""
        return ContentType(value=ContentTypeEnum.POST)
    
    @staticmethod
    def reel() -> 'ContentType':
        """Create reel content type."""
        return ContentType(value=ContentTypeEnum.REEL)
    
    @staticmethod
    def highlight() -> 'ContentType':
        """Create highlight content type."""
        return ContentType(value=ContentTypeEnum.HIGHLIGHT)
    
    @staticmethod
    def tagged_post() -> 'ContentType':
        """Create tagged post content type."""
        return ContentType(value=ContentTypeEnum.TAGGED_POST)
    
    def is_story(self) -> bool:
        """Check if content type is story."""
        return self.value == ContentTypeEnum.STORY
    
    def is_post(self) -> bool:
        """Check if content type is post."""
        return self.value == ContentTypeEnum.POST
    
    def is_reel(self) -> bool:
        """Check if content type is reel."""
        return self.value == ContentTypeEnum.REEL
    
    def is_highlight(self) -> bool:
        """Check if content type is highlight."""
        return self.value == ContentTypeEnum.HIGHLIGHT
    
    def is_tagged_post(self) -> bool:
        """Check if content type is tagged post."""
        return self.value == ContentTypeEnum.TAGGED_POST
    
    def __str__(self) -> str:
        """String representation."""
        return self.value.value
