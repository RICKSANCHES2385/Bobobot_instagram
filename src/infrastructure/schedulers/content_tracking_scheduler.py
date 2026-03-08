"""Content Tracking Scheduler."""

import asyncio
import logging
from typing import Optional
from datetime import datetime

from src.application.content_tracking.use_cases.check_content_updates import CheckContentUpdatesUseCase
from src.domain.content_tracking.repositories.content_tracking_repository import IContentTrackingRepository


logger = logging.getLogger(__name__)


class ContentTrackingScheduler:
    """Scheduler for checking content updates."""

    def __init__(
        self,
        repository: IContentTrackingRepository,
        check_updates_use_case: CheckContentUpdatesUseCase,
        check_interval_seconds: int = 60,
    ):
        """Initialize scheduler.
        
        Args:
            repository: Content tracking repository
            check_updates_use_case: Use case for checking updates
            check_interval_seconds: How often to check for trackings (default: 60s)
        """
        self._repository = repository
        self._check_updates_use_case = check_updates_use_case
        self._check_interval_seconds = check_interval_seconds
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start the scheduler."""
        if self._running:
            logger.warning("Scheduler is already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._run())
        logger.info("Content tracking scheduler started")

    async def stop(self) -> None:
        """Stop the scheduler."""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("Content tracking scheduler stopped")

    async def _run(self) -> None:
        """Main scheduler loop."""
        while self._running:
            try:
                await self._check_all_trackings()
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}", exc_info=True)

            # Wait before next check
            await asyncio.sleep(self._check_interval_seconds)

    async def _check_all_trackings(self) -> None:
        """Check all trackings that are due."""
        try:
            # Get trackings that should be checked
            trackings = await self._repository.find_trackings_to_check()

            if not trackings:
                logger.debug("No trackings to check")
                return

            logger.info(f"Checking {len(trackings)} trackings")

            # Check each tracking
            for tracking in trackings:
                try:
                    await self._check_updates_use_case.execute(tracking.tracking_id.value)
                    logger.debug(f"Checked tracking {tracking.tracking_id.value}")
                except Exception as e:
                    logger.error(
                        f"Error checking tracking {tracking.tracking_id.value}: {e}",
                        exc_info=True,
                    )

        except Exception as e:
            logger.error(f"Error getting trackings to check: {e}", exc_info=True)

    @property
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._running
