"""Rate limiting middleware."""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from src.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    """Middleware for rate limiting user requests."""

    def __init__(
        self,
        rate_limit: int = 30,  # requests per minute
        time_window: int = 60,  # seconds
    ):
        """Initialize rate limit middleware.
        
        Args:
            rate_limit: Maximum number of requests per time window
            time_window: Time window in seconds
        """
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.user_requests: Dict[int, list] = defaultdict(list)
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        """Check rate limit before processing request."""
        user = event.from_user
        if not user:
            return await handler(event, data)

        user_id = user.id
        now = datetime.now()

        # Clean old requests
        cutoff_time = now - timedelta(seconds=self.time_window)
        self.user_requests[user_id] = [
            req_time
            for req_time in self.user_requests[user_id]
            if req_time > cutoff_time
        ]

        # Check rate limit
        if len(self.user_requests[user_id]) >= self.rate_limit:
            logger.warning(f"Rate limit exceeded for user {user_id}")
            
            # Calculate wait time
            oldest_request = min(self.user_requests[user_id])
            wait_seconds = int((oldest_request + timedelta(seconds=self.time_window) - now).total_seconds())
            
            if isinstance(event, CallbackQuery):
                await event.answer(
                    f"⏳ Слишком много запросов. Подождите {wait_seconds} сек",
                    show_alert=True,
                )
            else:
                await event.answer(
                    f"⏳ <b>Превышен лимит запросов</b>\n\n"
                    f"Подождите {wait_seconds} секунд перед следующим запросом"
                )
            return

        # Add current request
        self.user_requests[user_id].append(now)

        # Process request
        return await handler(event, data)


class CommandRateLimitMiddleware(BaseMiddleware):
    """Middleware for rate limiting specific commands."""

    def __init__(self, limits: Dict[str, tuple[int, int]] = None):
        """Initialize command rate limit middleware.
        
        Args:
            limits: Dict of command -> (rate_limit, time_window) pairs
                   Example: {"/instagram": (5, 60)} = 5 requests per 60 seconds
        """
        self.limits = limits or {
            "/instagram": (10, 60),  # 10 requests per minute
            "/force": (3, 300),  # 3 requests per 5 minutes
        }
        self.user_command_requests: Dict[tuple[int, str], list] = defaultdict(list)
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        """Check command-specific rate limit."""
        if not event.from_user or not event.text:
            return await handler(event, data)

        user_id = event.from_user.id
        
        # Extract command
        command = None
        if event.text.startswith("/"):
            command = event.text.split()[0].split("@")[0]
        
        if not command or command not in self.limits:
            return await handler(event, data)

        rate_limit, time_window = self.limits[command]
        now = datetime.now()
        key = (user_id, command)

        # Clean old requests
        cutoff_time = now - timedelta(seconds=time_window)
        self.user_command_requests[key] = [
            req_time
            for req_time in self.user_command_requests[key]
            if req_time > cutoff_time
        ]

        # Check rate limit
        if len(self.user_command_requests[key]) >= rate_limit:
            logger.warning(f"Command rate limit exceeded for user {user_id}, command {command}")
            
            oldest_request = min(self.user_command_requests[key])
            wait_seconds = int((oldest_request + timedelta(seconds=time_window) - now).total_seconds())
            
            await event.answer(
                f"⏳ <b>Превышен лимит для команды {command}</b>\n\n"
                f"Подождите {wait_seconds} секунд перед следующим использованием"
            )
            return

        # Add current request
        self.user_command_requests[key].append(now)

        # Process request
        return await handler(event, data)
