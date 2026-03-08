"""Instagram Integration Domain Events."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.shared.events.base import DomainEvent


@dataclass(frozen=True)
class ProfileDataFetched(DomainEvent):
    """Event raised when Instagram profile data is fetched."""
    
    username: str = ""
    user_id: str = ""
    is_private: bool = False
    is_verified: bool = False
    followers: int = 0
    following: int = 0
    posts: int = 0


@dataclass(frozen=True)
class StoriesDataFetched(DomainEvent):
    """Event raised when Instagram stories data is fetched."""
    
    username: str = ""
    user_id: str = ""
    story_count: int = 0


@dataclass(frozen=True)
class PostsDataFetched(DomainEvent):
    """Event raised when Instagram posts data is fetched."""
    
    username: str = ""
    user_id: str = ""
    post_count: int = 0


@dataclass(frozen=True)
class ReelsDataFetched(DomainEvent):
    """Event raised when Instagram reels data is fetched."""
    
    username: str = ""
    user_id: str = ""
    reel_count: int = 0


@dataclass(frozen=True)
class HighlightsDataFetched(DomainEvent):
    """Event raised when Instagram highlights data is fetched."""
    
    username: str = ""
    user_id: str = ""
    highlight_count: int = 0


@dataclass(frozen=True)
class HighlightStoriesDataFetched(DomainEvent):
    """Event raised when Instagram highlight stories data is fetched."""
    
    username: str = ""
    highlight_id: str = ""
    story_count: int = 0


@dataclass(frozen=True)
class FollowersDataFetched(DomainEvent):
    """Event raised when Instagram followers data is fetched."""
    
    username: str = ""
    user_id: str = ""
    follower_count: int = 0


@dataclass(frozen=True)
class FollowingDataFetched(DomainEvent):
    """Event raised when Instagram following data is fetched."""
    
    username: str = ""
    user_id: str = ""
    following_count: int = 0


@dataclass(frozen=True)
class CommentsDataFetched(DomainEvent):
    """Event raised when Instagram comments data is fetched."""
    
    media_id: str = ""
    comment_count: int = 0


@dataclass(frozen=True)
class TaggedPostsDataFetched(DomainEvent):
    """Event raised when Instagram tagged posts data is fetched."""
    
    username: str = ""
    user_id: str = ""
    tagged_post_count: int = 0


@dataclass(frozen=True)
class ProfileNotFound(DomainEvent):
    """Event raised when Instagram profile is not found."""
    
    username: str = ""


@dataclass(frozen=True)
class ProfileIsPrivate(DomainEvent):
    """Event raised when Instagram profile is private."""
    
    username: str = ""
    user_id: str = ""
