"""Cache service for Instagram data."""

import json
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Optional

from ...infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class CacheService(ABC):
    """Abstract cache service interface."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with TTL in seconds."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass
    
    @abstractmethod
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        pass


class MemoryCacheService(CacheService):
    """In-memory cache service (fallback when Redis is not available)."""
    
    def __init__(self):
        """Initialize memory cache."""
        self._cache: dict[str, tuple[Any, Optional[float]]] = {}
        logger.info("Initialized in-memory cache service")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self._cache:
            return None
        
        value, expiry = self._cache[key]
        
        # Check expiry
        if expiry is not None:
            import time
            if time.time() > expiry:
                del self._cache[key]
                return None
        
        logger.debug(f"Cache hit: {key}")
        return value
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with TTL in seconds."""
        import time
        
        expiry = None
        if ttl is not None:
            expiry = time.time() + ttl
        
        self._cache[key] = (value, expiry)
        logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache delete: {key}")
            return True
        return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return key in self._cache
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        import fnmatch
        
        keys_to_delete = [
            key for key in self._cache.keys()
            if fnmatch.fnmatch(key, pattern)
        ]
        
        for key in keys_to_delete:
            del self._cache[key]
        
        logger.info(f"Cleared {len(keys_to_delete)} keys matching pattern: {pattern}")
        return len(keys_to_delete)


class RedisCacheService(CacheService):
    """Redis cache service."""
    
    def __init__(self, redis_url: str):
        """Initialize Redis cache."""
        try:
            import redis.asyncio as redis
            self.redis = redis.from_url(redis_url, decode_responses=True)
            logger.info(f"Initialized Redis cache service: {redis_url}")
        except ImportError:
            raise ImportError("redis package is required for RedisCacheService")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = await self.redis.get(key)
            if value is None:
                return None
            
            # Try to deserialize JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Error getting from Redis cache: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with TTL in seconds."""
        try:
            # Serialize to JSON if not string
            if not isinstance(value, str):
                value = json.dumps(value)
            
            if ttl is not None:
                await self.redis.setex(key, ttl, value)
            else:
                await self.redis.set(key, value)
            
            logger.debug(f"Redis cache set: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Error setting Redis cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            result = await self.redis.delete(key)
            logger.debug(f"Redis cache delete: {key}")
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting from Redis cache: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking Redis key existence: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        try:
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                deleted = await self.redis.delete(*keys)
                logger.info(f"Cleared {deleted} keys matching pattern: {pattern}")
                return deleted
            
            return 0
        except Exception as e:
            logger.error(f"Error clearing Redis pattern: {e}")
            return 0
    
    async def close(self):
        """Close Redis connection."""
        await self.redis.close()


def create_cache_service(redis_url: Optional[str] = None) -> CacheService:
    """Create cache service (Redis if available, otherwise in-memory)."""
    if redis_url:
        try:
            return RedisCacheService(redis_url)
        except Exception as e:
            logger.warning(f"Failed to initialize Redis cache: {e}. Using in-memory cache.")
    
    return MemoryCacheService()
