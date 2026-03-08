"""Rate limiting service for user requests."""

from datetime import datetime

from src.infrastructure.cache.cache_service import CacheService
from src.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class RateLimitService:
    """Service for rate limiting user requests."""
    
    # Rate limits
    REQUESTS_PER_MINUTE = 10
    REQUESTS_PER_DAY = 100
    
    def __init__(self, cache_service: CacheService):
        """Initialize rate limit service.
        
        Args:
            cache_service: Cache service for storing counters
        """
        self.cache = cache_service
    
    async def check_minute_limit(self, user_id: int) -> tuple[bool, int]:
        """Check if user exceeded rate limit for current minute.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Tuple of (is_allowed, requests_count)
        """
        now = datetime.utcnow()
        minute_key = f"rate_limit:user:{user_id}:minute:{now.strftime('%Y%m%d%H%M')}"
        
        try:
            # Get current count
            count_str = await self.cache.get(minute_key)
            count = int(count_str) if count_str else 0
            
            # Increment
            count += 1
            await self.cache.set(minute_key, str(count), ttl=60)
            
            is_allowed = count <= self.REQUESTS_PER_MINUTE
            return is_allowed, count
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return True, 0  # Allow on error
    
    async def check_day_limit(self, user_id: int) -> tuple[bool, int]:
        """Check if user exceeded rate limit for current day.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Tuple of (is_allowed, requests_count)
        """
        now = datetime.utcnow()
        day_key = f"rate_limit:user:{user_id}:day:{now.strftime('%Y%m%d')}"
        
        try:
            # Get current count
            count_str = await self.cache.get(day_key)
            count = int(count_str) if count_str else 0
            
            # Increment
            count += 1
            await self.cache.set(day_key, str(count), ttl=86400)
            
            is_allowed = count <= self.REQUESTS_PER_DAY
            return is_allowed, count
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return True, 0  # Allow on error
    
    async def check_limits(self, user_id: int) -> tuple[bool, str]:
        """Check both minute and day limits.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Tuple of (is_allowed, error_message)
        """
        # Check minute limit
        minute_ok, minute_count = await self.check_minute_limit(user_id)
        if not minute_ok:
            return (
                False,
                f"⏱ Превышен лимит запросов в минуту ({minute_count}/{self.REQUESTS_PER_MINUTE})\n\n"
                f"Подождите немного и попробуйте снова"
            )
        
        # Check day limit
        day_ok, day_count = await self.check_day_limit(user_id)
        if not day_ok:
            return (
                False,
                f"⏱ Превышен дневной лимит запросов ({day_count}/{self.REQUESTS_PER_DAY})\n\n"
                f"Попробуйте завтра"
            )
        
        return (True, "")
    
    async def get_remaining_requests(self, user_id: int) -> dict[str, int]:
        """Get remaining requests for user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Dict with remaining requests per minute and per day
        """
        now = datetime.utcnow()
        minute_key = f"rate_limit:user:{user_id}:minute:{now.strftime('%Y%m%d%H%M')}"
        day_key = f"rate_limit:user:{user_id}:day:{now.strftime('%Y%m%d')}"
        
        try:
            minute_count_str = await self.cache.get(minute_key)
            day_count_str = await self.cache.get(day_key)
            
            minute_count = int(minute_count_str) if minute_count_str else 0
            day_count = int(day_count_str) if day_count_str else 0
            
            return {
                "minute": max(0, self.REQUESTS_PER_MINUTE - minute_count),
                "day": max(0, self.REQUESTS_PER_DAY - day_count),
            }
        except Exception as e:
            logger.error(f"Get remaining requests error: {e}")
            return {"minute": 0, "day": 0}
