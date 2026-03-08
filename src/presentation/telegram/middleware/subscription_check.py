"""Subscription check middleware."""

from typing import Any, Awaitable, Callable, Dict, List

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from src.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class SubscriptionCheckMiddleware(BaseMiddleware):
    """Middleware to check user subscription before processing requests."""

    def __init__(self, exempt_commands: List[str] = None):
        """Initialize subscription check middleware.
        
        Args:
            exempt_commands: List of commands that don't require subscription
        """
        self.exempt_commands = exempt_commands or [
            "/start",
            "/help",
            "/tariffs",
            "/buy",
            "/support",
        ]
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        """Check subscription and call handler."""
        user = event.from_user
        if not user:
            return await handler(event, data)

        # Check if command is exempt
        if isinstance(event, Message) and event.text:
            if event.text.startswith("/"):
                command = event.text.split()[0].split("@")[0]
                if command in self.exempt_commands:
                    return await handler(event, data)

        # Check if callback is exempt (payment-related)
        if isinstance(event, CallbackQuery) and event.data:
            exempt_callbacks = [
                "back_to_start",
                "tariffs_menu",
                "buy_subscription",
                "payment_",
                "buy_",
                "robokassa_",
                "crypto_",
                "support",
                "partnership",
            ]
            if any(event.data.startswith(prefix) for prefix in exempt_callbacks):
                return await handler(event, data)

        # TODO: Implement subscription check via CheckSubscriptionStatusUseCase
        # For now, just pass through
        # In production:
        # 1. Get user subscription from database
        # 2. Check if subscription is active
        # 3. If not active, show subscription required message
        # 4. If active, continue to handler

        # Example implementation:
        # subscription = await check_subscription_use_case.execute(user.id)
        # if not subscription or not subscription.is_active:
        #     if isinstance(event, CallbackQuery):
        #         await event.answer("Требуется активная подписка", show_alert=True)
        #     else:
        #         await event.answer(
        #             "❌ <b>Требуется подписка</b>\n\n"
        #             "Используйте /buy для покупки подписки"
        #         )
        #     return

        return await handler(event, data)


class FeatureAccessMiddleware(BaseMiddleware):
    """Middleware to check access to premium features."""

    def __init__(self, premium_callbacks: List[str] = None):
        """Initialize feature access middleware.
        
        Args:
            premium_callbacks: List of callback prefixes that require premium
        """
        self.premium_callbacks = premium_callbacks or [
            "track_audience_",
            "ig_followers_dl_",
            "ig_following_dl_",
            "ig_posts_dl_",
            "ig_reels_dl_",
        ]
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        """Check feature access and call handler."""
        if not event.from_user or not event.data:
            return await handler(event, data)

        # Check if callback requires premium
        is_premium_feature = any(
            event.data.startswith(prefix) for prefix in self.premium_callbacks
        )

        if not is_premium_feature:
            return await handler(event, data)

        # TODO: Check if user has premium subscription
        # For now, just pass through
        # In production:
        # 1. Get user subscription from database
        # 2. Check if subscription plan includes this feature
        # 3. If not, show upgrade message

        return await handler(event, data)
