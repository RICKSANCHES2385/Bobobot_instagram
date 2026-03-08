"""Profile Statistics Value Object."""
from dataclasses import dataclass

from src.domain.shared.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class ProfileStatistics(BaseValueObject):
    """Instagram profile statistics value object."""
    
    followers: int
    following: int
    posts: int
    
    def __post_init__(self):
        """Validate statistics."""
        if self.followers < 0:
            raise ValueError("Followers count cannot be negative")
        
        if self.following < 0:
            raise ValueError("Following count cannot be negative")
        
        if self.posts < 0:
            raise ValueError("Posts count cannot be negative")
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.posts} posts, {self.followers} followers, {self.following} following"
    
    def has_followers(self) -> bool:
        """Check if profile has followers."""
        return self.followers > 0
    
    def has_posts(self) -> bool:
        """Check if profile has posts."""
        return self.posts > 0
