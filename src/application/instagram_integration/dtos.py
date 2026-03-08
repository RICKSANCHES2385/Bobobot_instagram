"""Instagram Integration DTOs."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class InstagramProfileDTO:
    """Instagram profile data transfer object."""
    
    username: str
    user_id: str
    full_name: str
    bio: str
    followers: int
    following: int
    posts: int
    is_private: bool
    is_verified: bool
    profile_pic_url: Optional[str] = None
    external_url: Optional[str] = None


@dataclass
class InstagramStoryDTO:
    """Instagram story data transfer object."""
    
    media_id: str
    user_id: str
    media_url: str
    media_type: str
    taken_at: datetime
    expires_at: Optional[datetime] = None


@dataclass
class InstagramPostDTO:
    """Instagram post data transfer object."""
    
    media_id: str
    user_id: str
    media_urls: List[str]
    caption: str
    media_type: str
    like_count: int
    comment_count: int
    taken_at: datetime


@dataclass
class InstagramReelDTO:
    """Instagram reel data transfer object."""
    
    media_id: str
    user_id: str
    video_url: str
    caption: str
    thumbnail_url: Optional[str]
    like_count: int
    comment_count: int
    play_count: int
    taken_at: datetime


@dataclass
class InstagramHighlightDTO:
    """Instagram highlight data transfer object."""
    
    highlight_id: str
    user_id: str
    title: str
    cover_url: str
    story_count: int


@dataclass
class InstagramCommentDTO:
    """Instagram comment data transfer object."""
    
    comment_id: str
    media_id: str
    user_id: str
    username: str
    text: str
    like_count: int
    created_at: datetime


@dataclass
class FollowerDTO:
    """Follower data transfer object."""
    
    user_id: str
    username: str
    full_name: str
    profile_pic_url: Optional[str] = None
    is_verified: bool = False


@dataclass
class FollowersListDTO:
    """Followers list data transfer object."""
    
    username: str
    user_id: str
    followers: List[FollowerDTO]
    total_count: int
    has_more: bool = False


@dataclass
class FollowingListDTO:
    """Following list data transfer object."""
    
    username: str
    user_id: str
    following: List[FollowerDTO]
    total_count: int
    has_more: bool = False
