"""Request type value object."""

from dataclasses import dataclass
from enum import Enum

from ...shared.value_objects.base import BaseValueObject


class RequestTypeEnum(str, Enum):
    """Request type enumeration."""
    
    PROFILE = "profile"
    STORIES = "stories"
    POSTS = "posts"
    REELS = "reels"
    HIGHLIGHTS = "highlights"
    HIGHLIGHT_STORIES = "highlight_stories"
    FOLLOWERS = "followers"
    FOLLOWING = "following"
    TAGGED_POSTS = "tagged_posts"


@dataclass(frozen=True)
class RequestType(BaseValueObject):
    """Request type value object."""
    
    value: RequestTypeEnum
    
    @staticmethod
    def profile() -> 'RequestType':
        """Create profile request type."""
        return RequestType(value=RequestTypeEnum.PROFILE)
    
    @staticmethod
    def stories() -> 'RequestType':
        """Create stories request type."""
        return RequestType(value=RequestTypeEnum.STORIES)
    
    @staticmethod
    def posts() -> 'RequestType':
        """Create posts request type."""
        return RequestType(value=RequestTypeEnum.POSTS)
    
    @staticmethod
    def reels() -> 'RequestType':
        """Create reels request type."""
        return RequestType(value=RequestTypeEnum.REELS)
    
    @staticmethod
    def highlights() -> 'RequestType':
        """Create highlights request type."""
        return RequestType(value=RequestTypeEnum.HIGHLIGHTS)
    
    @staticmethod
    def highlight_stories() -> 'RequestType':
        """Create highlight stories request type."""
        return RequestType(value=RequestTypeEnum.HIGHLIGHT_STORIES)
    
    @staticmethod
    def followers() -> 'RequestType':
        """Create followers request type."""
        return RequestType(value=RequestTypeEnum.FOLLOWERS)
    
    @staticmethod
    def following() -> 'RequestType':
        """Create following request type."""
        return RequestType(value=RequestTypeEnum.FOLLOWING)
    
    @staticmethod
    def tagged_posts() -> 'RequestType':
        """Create tagged posts request type."""
        return RequestType(value=RequestTypeEnum.TAGGED_POSTS)
