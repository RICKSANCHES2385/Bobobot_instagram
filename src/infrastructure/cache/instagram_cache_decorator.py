"""Cache decorator for Instagram API calls."""

import hashlib
import json
from functools import wraps
from typing import Any, Callable, Optional

from .cache_service import CacheService
from ...infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class InstagramCacheDecorator:
    """Decorator for caching Instagram API responses."""
    
    # Default TTL values (in seconds)
    TTL_PROFILE = 300  # 5 minutes
    TTL_STORIES = 180  # 3 minutes
    TTL_POSTS = 600  # 10 minutes
    TTL_FOLLOWERS = 3600  # 1 hour
    TTL_FOLLOWING = 3600  # 1 hour
    
    def __init__(self, cache_service: CacheService):
        """Initialize cache decorator."""
        self.cache_service = cache_service
    
    def _generate_cache_key(
        self,
        prefix: str,
        *args,
        **kwargs
    ) -> str:
        """Generate cache key from function arguments."""
        # Create a string representation of arguments
        key_parts = [prefix]
        
        # Add positional arguments
        for arg in args:
            if isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
        
        # Add keyword arguments (sorted for consistency)
        for k, v in sorted(kwargs.items()):
            if isinstance(v, (str, int, float, bool)):
                key_parts.append(f"{k}={v}")
        
        # Join and hash if too long
        key = ":".join(key_parts)
        if len(key) > 200:
            key_hash = hashlib.md5(key.encode()).hexdigest()
            key = f"{prefix}:{key_hash}"
        
        return key
    
    def cache_profile(
        self,
        ttl: Optional[int] = None
    ) -> Callable:
        """Cache Instagram profile data."""
        if ttl is None:
            ttl = self.TTL_PROFILE
        
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                # Generate cache key
                cache_key = self._generate_cache_key(
                    "instagram:profile",
                    *args,
                    **kwargs
                )
                
                # Try to get from cache
                cached_value = await self.cache_service.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit for profile: {cache_key}")
                    return cached_value
                
                # Call original function
                result = await func(*args, **kwargs)
                
                # Store in cache
                if result is not None:
                    await self.cache_service.set(cache_key, result, ttl)
                    logger.debug(f"Cached profile: {cache_key}")
                
                return result
            
            return wrapper
        return decorator
    
    def cache_stories(
        self,
        ttl: Optional[int] = None
    ) -> Callable:
        """Cache Instagram stories data."""
        if ttl is None:
            ttl = self.TTL_STORIES
        
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                cache_key = self._generate_cache_key(
                    "instagram:stories",
                    *args,
                    **kwargs
                )
                
                cached_value = await self.cache_service.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit for stories: {cache_key}")
                    return cached_value
                
                result = await func(*args, **kwargs)
                
                if result is not None:
                    await self.cache_service.set(cache_key, result, ttl)
                    logger.debug(f"Cached stories: {cache_key}")
                
                return result
            
            return wrapper
        return decorator
    
    def cache_posts(
        self,
        ttl: Optional[int] = None
    ) -> Callable:
        """Cache Instagram posts data."""
        if ttl is None:
            ttl = self.TTL_POSTS
        
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                cache_key = self._generate_cache_key(
                    "instagram:posts",
                    *args,
                    **kwargs
                )
                
                cached_value = await self.cache_service.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit for posts: {cache_key}")
                    return cached_value
                
                result = await func(*args, **kwargs)
                
                if result is not None:
                    await self.cache_service.set(cache_key, result, ttl)
                    logger.debug(f"Cached posts: {cache_key}")
                
                return result
            
            return wrapper
        return decorator
    
    def cache_followers(
        self,
        ttl: Optional[int] = None
    ) -> Callable:
        """Cache Instagram followers list."""
        if ttl is None:
            ttl = self.TTL_FOLLOWERS
        
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                cache_key = self._generate_cache_key(
                    "instagram:followers",
                    *args,
                    **kwargs
                )
                
                cached_value = await self.cache_service.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit for followers: {cache_key}")
                    return cached_value
                
                result = await func(*args, **kwargs)
                
                if result is not None:
                    await self.cache_service.set(cache_key, result, ttl)
                    logger.debug(f"Cached followers: {cache_key}")
                
                return result
            
            return wrapper
        return decorator
    
    def cache_following(
        self,
        ttl: Optional[int] = None
    ) -> Callable:
        """Cache Instagram following list."""
        if ttl is None:
            ttl = self.TTL_FOLLOWING
        
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                cache_key = self._generate_cache_key(
                    "instagram:following",
                    *args,
                    **kwargs
                )
                
                cached_value = await self.cache_service.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit for following: {cache_key}")
                    return cached_value
                
                result = await func(*args, **kwargs)
                
                if result is not None:
                    await self.cache_service.set(cache_key, result, ttl)
                    logger.debug(f"Cached following: {cache_key}")
                
                return result
            
            return wrapper
        return decorator
    
    async def invalidate_user_cache(self, username: str) -> int:
        """Invalidate all cache entries for a user."""
        patterns = [
            f"instagram:profile:*{username}*",
            f"instagram:stories:*{username}*",
            f"instagram:posts:*{username}*",
            f"instagram:followers:*{username}*",
            f"instagram:following:*{username}*",
        ]
        
        total_deleted = 0
        for pattern in patterns:
            deleted = await self.cache_service.clear_pattern(pattern)
            total_deleted += deleted
        
        logger.info(f"Invalidated {total_deleted} cache entries for user: {username}")
        return total_deleted
