"""Audience Tracking Checker Background Task."""

import asyncio
from datetime import datetime
from typing import List

from aiogram import Bot

from src.application.audience_tracking.use_cases.check_audience_changes import (
    CheckAudienceChangesUseCase,
)
from src.application.audience_tracking.dtos import AudienceChangeDTO
from src.domain.audience_tracking.repositories.audience_tracking_repository import (
    AudienceTrackingRepository,
)
from src.presentation.telegram.formatters.audience_tracking_formatter import (
    AudienceTrackingFormatter,
)
from src.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class AudienceTrackingChecker:
    """Background task for checking audience changes."""

    def __init__(
        self,
        bot: Bot,
        tracking_repository: AudienceTrackingRepository,
        check_audience_changes_use_case: CheckAudienceChangesUseCase,
        check_interval_seconds: int = 3600,  # 1 hour default
    ):
        """Initialize checker.
        
        Args:
            bot: Telegram bot instance
            tracking_repository: Audience tracking repository
            check_audience_changes_use_case: Use case for checking changes
            check_interval_seconds: Check interval in seconds
        """
        self.bot = bot
        self.tracking_repository = tracking_repository
        self.check_audience_changes_use_case = check_audience_changes_use_case
        self.check_interval_seconds = check_interval_seconds
        self.is_running = False
        self.task = None

    async def start(self) -> None:
        """Start the checker task."""
        if self.is_running:
            logger.warning("Audience tracking checker is already running")
            return

        self.is_running = True
        self.task = asyncio.create_task(self._run())
        logger.info("Audience tracking checker started")

    async def stop(self) -> None:
        """Stop the checker task."""
        if not self.is_running:
            return

        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        logger.info("Audience tracking checker stopped")

    async def _run(self) -> None:
        """Main checker loop."""
        logger.info("Audience tracking checker loop started")
        
        while self.is_running:
            try:
                await self._check_all_trackings()
            except Exception as e:
                logger.error(f"Error in audience tracking checker: {e}", exc_info=True)
            
            # Wait for next check
            await asyncio.sleep(self.check_interval_seconds)

    async def _check_all_trackings(self) -> None:
        """Check all active trackings."""
        logger.info("Checking all active audience trackings")
        
        try:
            # Get all active trackings
            # Note: We need to get all users' active trackings
            # For now, we'll implement a method to get all active trackings
            # This should be added to the repository interface
            
            # Placeholder: In production, implement get_all_active_trackings()
            # trackings = await self.tracking_repository.get_all_active_trackings()
            
            # For now, log that we would check
            logger.info("Would check active trackings here")
            
            # TODO: Implement actual checking logic
            # for tracking in trackings:
            #     await self._check_tracking(tracking.tracking_id.value)
            
        except Exception as e:
            logger.error(f"Error checking trackings: {e}", exc_info=True)

    async def _check_tracking(self, tracking_id: int) -> None:
        """Check single tracking for changes.
        
        Args:
            tracking_id: Tracking ID
        """
        try:
            logger.debug(f"Checking tracking {tracking_id}")
            
            # Check for changes
            changes = await self.check_audience_changes_use_case.execute(tracking_id)
            
            if changes:
                logger.info(f"Found {len(changes)} changes for tracking {tracking_id}")
                
                # Send notifications
                for change in changes:
                    await self._send_change_notification(change)
            else:
                logger.debug(f"No changes for tracking {tracking_id}")
                
        except Exception as e:
            logger.error(f"Error checking tracking {tracking_id}: {e}", exc_info=True)

    async def _send_change_notification(self, change: AudienceChangeDTO) -> None:
        """Send change notification to user.
        
        Args:
            change: Change DTO
        """
        try:
            text = AudienceTrackingFormatter.format_change_notification(change)
            
            await self.bot.send_message(
                chat_id=change.user_id,
                text=text,
                parse_mode="HTML"
            )
            
            logger.info(
                f"Sent change notification to user {change.user_id} "
                f"for @{change.target_username}"
            )
            
        except Exception as e:
            logger.error(
                f"Error sending notification to user {change.user_id}: {e}",
                exc_info=True
            )

    async def check_tracking_now(self, tracking_id: int) -> List[AudienceChangeDTO]:
        """Manually trigger check for specific tracking.
        
        Args:
            tracking_id: Tracking ID
            
        Returns:
            List of detected changes
        """
        logger.info(f"Manual check triggered for tracking {tracking_id}")
        
        changes = await self.check_audience_changes_use_case.execute(tracking_id)
        
        if changes:
            for change in changes:
                await self._send_change_notification(change)
        
        return changes
