"""Main Telegram bot application with DDD architecture."""

import asyncio
import logging
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.infrastructure.config import Settings, get_settings
from src.infrastructure.logging.logger import get_logger
from src.presentation.telegram.dependencies import init_container, get_container
from src.presentation.telegram.handlers import (
    register_command_handlers,
    register_instagram_handlers,
    register_payment_handlers,
    register_tracking_handlers,
    register_audience_tracking_handlers,
)
from src.presentation.telegram.middleware.subscription_check import SubscriptionCheckMiddleware
from src.presentation.telegram.middleware.rate_limit import RateLimitMiddleware
from src.presentation.telegram.tasks.tracking_checker import TrackingChecker
from src.presentation.telegram.tasks.notification_sender import NotificationSender
from src.presentation.telegram.tasks.cleanup_tasks import CleanupTasks

logger = get_logger(__name__)


class TelegramBot:
    """Telegram bot application."""

    def __init__(self, settings: Settings) -> None:
        """Initialize bot."""
        self.settings = settings
        self.bot = Bot(
            token=settings.telegram_bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        self.storage = MemoryStorage()
        self.dp = Dispatcher(storage=self.storage)
        
        # Initialize database
        self._init_database()
        
        # Initialize dependency container
        self._init_dependencies()
        
        # Initialize background tasks (skip in test environment)
        if settings.environment != "test":
            self._init_background_tasks()
        
        # Register middleware
        self._register_middleware()
        
        # Register handlers
        self._register_handlers()
    
    def _init_database(self) -> None:
        """Initialize database connection."""
        # Convert sync sqlite URL to async for tests
        database_url = self.settings.database_url
        if database_url.startswith("sqlite://"):
            database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        
        # SQLite doesn't support pool_size and max_overflow
        engine_kwargs = {
            "echo": self.settings.environment == "development",
            "pool_pre_ping": True,
        }
        
        # Only add pooling for non-SQLite databases
        if not database_url.startswith("sqlite"):
            engine_kwargs["pool_size"] = 10
            engine_kwargs["max_overflow"] = 20
        
        self.engine = create_async_engine(
            database_url,
            **engine_kwargs
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
        )
        logger.info("Database initialized")
    
    def _init_dependencies(self) -> None:
        """Initialize dependency injection container."""
        init_container(
            session_factory=self.session_factory,
            hiker_api_key=self.settings.hikerapi_key,
            telegram_bot_token=self.settings.telegram_bot_token,
            cryptobot_token=self.settings.cryptobot_token if self.settings.cryptobot_token else None,
        )
        logger.info("Dependency container initialized")
    
    def _init_background_tasks(self) -> None:
        """Initialize background tasks."""
        container = get_container()
        
        # Initialize tracking checker
        self.tracking_checker = TrackingChecker(
            bot=self.bot,
            check_interval_seconds=300,  # Check every 5 minutes
        )
        
        # Initialize notification sender
        self.notification_sender = NotificationSender(
            bot=self.bot,
        )
        
        # Initialize cleanup tasks
        self.cleanup_tasks = CleanupTasks(
            cleanup_interval_seconds=86400,  # Cleanup every 24 hours
        )
        
        logger.info("Background tasks initialized")

    def _register_middleware(self) -> None:
        """Register middleware."""
        # Rate limiting middleware
        self.dp.message.middleware(RateLimitMiddleware())
        self.dp.callback_query.middleware(RateLimitMiddleware())
        
        # Subscription check middleware
        self.dp.message.middleware(SubscriptionCheckMiddleware())
        self.dp.callback_query.middleware(SubscriptionCheckMiddleware())
        
        logger.info("Middleware registered")

    def _register_handlers(self) -> None:
        """Register all handlers."""
        register_command_handlers(self.dp)
        register_instagram_handlers(self.dp)
        register_tracking_handlers(self.dp)
        register_audience_tracking_handlers(self.dp)
        register_payment_handlers(self.dp)
        logger.info("Handlers registered")

    async def start(self) -> None:
        """Start bot polling."""
        logger.info("Starting Telegram bot...")
        logger.info(f"Environment: {self.settings.environment}")
        
        try:
            # Set bot commands
            await self._set_bot_commands()
            
            # Start background tasks
            await self._start_background_tasks()
            
            # Start polling
            await self.dp.start_polling(
                self.bot,
                allowed_updates=["message", "callback_query"],
            )
        except Exception as e:
            logger.exception(f"Error starting bot: {e}")
            raise
        finally:
            await self._stop_background_tasks()
            await self.bot.session.close()

    async def stop(self) -> None:
        """Stop bot."""
        logger.info("Stopping Telegram bot...")
        await self._stop_background_tasks()
        await self.dp.stop_polling()
        await self.bot.session.close()
        await self.engine.dispose()
        logger.info("Bot stopped")
    
    async def _start_background_tasks(self) -> None:
        """Start background tasks."""
        if self.settings.environment == "test":
            return
        logger.info("Starting background tasks...")
        await self.tracking_checker.start()
        await self.notification_sender.start()
        await self.cleanup_tasks.start()
        logger.info("Background tasks started")
    
    async def _stop_background_tasks(self) -> None:
        """Stop background tasks."""
        if self.settings.environment == "test":
            return
        logger.info("Stopping background tasks...")
        await self.tracking_checker.stop()
        await self.notification_sender.stop()
        await self.cleanup_tasks.stop()
        logger.info("Background tasks stopped")

    async def _set_bot_commands(self) -> None:
        """Set bot commands menu."""
        from aiogram.types import BotCommand

        commands = [
            BotCommand(command="start", description="🏠 Перезапустить бота"),
            BotCommand(command="tariffs", description="👑 Тарифы Безлимит"),
            BotCommand(command="sub", description="📊 Мои отслеживания"),
            BotCommand(command="force", description="🔄 Обновления"),
            BotCommand(command="ref", description="👥 Партнёрка"),
            BotCommand(command="support", description="🏛 Поддержка"),
        ]

        try:
            await self.bot.set_my_commands(commands)
            logger.info("Bot commands set successfully")
        except Exception as e:
            logger.warning(f"Failed to set bot commands: {e}")


async def main() -> None:
    """Run bot."""
    settings = get_settings()
    bot = TelegramBot(settings)
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
