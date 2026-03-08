"""Tests for Content Tracking Scheduler."""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock
from datetime import datetime, timedelta

from src.infrastructure.schedulers.content_tracking_scheduler import ContentTrackingScheduler
from src.domain.content_tracking.aggregates.content_tracking import ContentTracking
from src.domain.content_tracking.value_objects.tracking_id import TrackingId
from src.domain.content_tracking.value_objects.content_type import ContentType, ContentTypeEnum
from src.domain.content_tracking.value_objects.check_interval import CheckInterval
from src.domain.instagram_integration.value_objects.instagram_user_id import InstagramUserId
from src.domain.instagram_integration.value_objects.instagram_username import InstagramUsername


@pytest.fixture
def mock_repository():
    """Create mock repository."""
    return AsyncMock()


@pytest.fixture
def mock_check_updates_use_case():
    """Create mock use case."""
    return AsyncMock()


@pytest.fixture
def scheduler(mock_repository, mock_check_updates_use_case):
    """Create scheduler instance."""
    return ContentTrackingScheduler(
        repository=mock_repository,
        check_updates_use_case=mock_check_updates_use_case,
        check_interval_seconds=1,  # Short interval for testing
    )


@pytest.fixture
def sample_tracking():
    """Create sample tracking."""
    tracking = ContentTracking.create(
        tracking_id=TrackingId.generate(),
        user_id="123456789",
        instagram_user_id=InstagramUserId("987654321"),
        instagram_username=InstagramUsername("test_user"),
        content_type=ContentType(ContentTypeEnum.POSTS),
        check_interval=CheckInterval(30),
    )
    # Set last check to 31 minutes ago so it should be checked
    tracking.last_check_at = datetime.utcnow() - timedelta(minutes=31)
    return tracking


@pytest.mark.asyncio
class TestContentTrackingScheduler:
    """Test content tracking scheduler."""

    async def test_start_scheduler(self, scheduler):
        """Test starting scheduler."""
        # Act
        await scheduler.start()

        # Assert
        assert scheduler.is_running
        assert scheduler._task is not None

        # Cleanup
        await scheduler.stop()

    async def test_stop_scheduler(self, scheduler):
        """Test stopping scheduler."""
        # Arrange
        await scheduler.start()

        # Act
        await scheduler.stop()

        # Assert
        assert not scheduler.is_running

    async def test_start_already_running(self, scheduler):
        """Test starting already running scheduler."""
        # Arrange
        await scheduler.start()

        # Act
        await scheduler.start()  # Should not raise

        # Assert
        assert scheduler.is_running

        # Cleanup
        await scheduler.stop()

    async def test_check_trackings(
        self,
        scheduler,
        mock_repository,
        mock_check_updates_use_case,
        sample_tracking,
    ):
        """Test checking trackings."""
        # Arrange
        mock_repository.find_trackings_to_check.return_value = [sample_tracking]

        # Act
        await scheduler._check_all_trackings()

        # Assert
        mock_repository.find_trackings_to_check.assert_called_once()
        mock_check_updates_use_case.execute.assert_called_once_with(
            sample_tracking.tracking_id.value
        )

    async def test_check_no_trackings(
        self,
        scheduler,
        mock_repository,
        mock_check_updates_use_case,
    ):
        """Test checking when no trackings are due."""
        # Arrange
        mock_repository.find_trackings_to_check.return_value = []

        # Act
        await scheduler._check_all_trackings()

        # Assert
        mock_repository.find_trackings_to_check.assert_called_once()
        mock_check_updates_use_case.execute.assert_not_called()

    async def test_check_multiple_trackings(
        self,
        scheduler,
        mock_repository,
        mock_check_updates_use_case,
    ):
        """Test checking multiple trackings."""
        # Arrange
        tracking1 = ContentTracking.create(
            tracking_id=TrackingId.generate(),
            user_id="user1",
            instagram_user_id=InstagramUserId("ig1"),
            instagram_username=InstagramUsername("ig_user1"),
            content_type=ContentType(ContentTypeEnum.POSTS),
            check_interval=CheckInterval(30),
        )
        tracking2 = ContentTracking.create(
            tracking_id=TrackingId.generate(),
            user_id="user2",
            instagram_user_id=InstagramUserId("ig2"),
            instagram_username=InstagramUsername("ig_user2"),
            content_type=ContentType(ContentTypeEnum.STORIES),
            check_interval=CheckInterval(15),
        )

        mock_repository.find_trackings_to_check.return_value = [tracking1, tracking2]

        # Act
        await scheduler._check_all_trackings()

        # Assert
        assert mock_check_updates_use_case.execute.call_count == 2

    async def test_error_handling_in_check(
        self,
        scheduler,
        mock_repository,
        mock_check_updates_use_case,
        sample_tracking,
    ):
        """Test error handling during check."""
        # Arrange
        mock_repository.find_trackings_to_check.return_value = [sample_tracking]
        mock_check_updates_use_case.execute.side_effect = Exception("Test error")

        # Act - should not raise
        await scheduler._check_all_trackings()

        # Assert
        mock_check_updates_use_case.execute.assert_called_once()

    async def test_scheduler_loop_runs(
        self,
        scheduler,
        mock_repository,
    ):
        """Test that scheduler loop runs periodically."""
        # Arrange
        mock_repository.find_trackings_to_check.return_value = []

        # Act
        await scheduler.start()
        await asyncio.sleep(2.5)  # Wait for at least 2 iterations
        await scheduler.stop()

        # Assert - should be called at least twice
        assert mock_repository.find_trackings_to_check.call_count >= 2
