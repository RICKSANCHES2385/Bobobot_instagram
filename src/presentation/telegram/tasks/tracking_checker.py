"""Background task for checking content tracking updates."""

import asyncio
from datetime import datetime, timedelta
from typing import Optional

from aiogram import Bot

from src.infrastructure.logging.logger import get_logger
from src.presentation.telegram.dependencies import get_container
from src.application.content_tracking.use_cases.check_content_updates import CheckContentUpdatesUseCase

logger = get_logger(__name__)


class TrackingChecker:
    """Check content tracking updates periodically."""
    
    def __init__(self, bot: Bot, check_interval_seconds: int = 300):
        """Initialize checker.
        
        Args:
            bot: Telegram bot instance
            check_interval_seconds: Interval between checks (default 5 minutes)
        """
        self.bot = bot
        self.check_interval_seconds = check_interval_seconds
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start background checking."""
        if self.is_running:
            logger.warning("Tracking checker already running")
            return
        
        self.is_running = True
        self._task = asyncio.create_task(self._check_loop())
        logger.info(f"Tracking checker started (interval: {self.check_interval_seconds}s)")
    
    async def stop(self):
        """Stop background checking."""
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Tracking checker stopped")
    
    async def _check_loop(self):
        """Main checking loop."""
        while self.is_running:
            try:
                await self._check_all_trackings()
            except Exception as e:
                logger.error(f"Error in tracking check loop: {e}")
            
            # Wait for next check
            await asyncio.sleep(self.check_interval_seconds)
    
    async def _check_all_trackings(self):
        """Check all active trackings."""
        logger.debug("Checking all active trackings...")
        
        # Get use cases
        container = get_container()
        use_cases = container.get_use_cases()
        
        try:
            # This would need a new use case to get all active trackings
            # For now, we'll skip the implementation
            # In production, you'd want:
            # 1. Get all active trackings that need checking
            # 2. For each tracking, call CheckContentUpdatesUseCase
            # 3. Send notifications for new content
            
            logger.debug("Tracking check completed")
            
        except Exception as e:
            logger.error(f"Error checking trackings: {e}")
    
    async def check_tracking(self, tracking_id: int):
        """Check specific tracking for updates.
        
        Args:
            tracking_id: Tracking ID to check
        """
        logger.info(f"Checking tracking {tracking_id}")
        
        # Get use cases
        container = get_container()
        use_cases = container.get_use_cases()
        
        try:
            # Check for updates
            # updates = await use_cases.check_content_updates.execute(tracking_id)
            
            # Send notifications if there are updates
            # if updates:
            #     await self._send_notifications(tracking_id, updates)
            
            pass
            
        except Exception as e:
            logger.error(f"Error checking tracking {tracking_id}: {e}")
    
    async def _send_notifications(self, tracking_id: int, updates: list):
        """Send notifications for content updates.
        
        Args:
            tracking_id: Tracking ID
            updates: List of content updates
        """
        # This would send notifications to users
        # Implementation depends on notification format
        pass
