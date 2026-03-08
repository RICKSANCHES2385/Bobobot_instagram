"""Tests for SQLAlchemy Content Tracking Repository."""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.content_tracking.aggregates.content_tracking import ContentTracking
from src.domain.content_tracking.value_objects.tracking_id import TrackingId
from src.domain.content_tracking.value_objects.content_type import ContentType, ContentTypeEnum
from src.domain.content_tracking.value_objects.check_interval import CheckInterval
from src.domain.instagram_integration.value_objects.instagram_user_id import InstagramUserId
from src.domain.instagram_integration.value_objects.instagram_username import InstagramUsername
from src.infrastructure.persistence.repositories.sqlalchemy_content_tracking_repository import (
    SQLAlchemyContentTrackingRepository,
)


@pytest.fixture
def repository(async_session: AsyncSession):
    """Create repository instance."""
    return SQLAlchemyContentTrackingRepository(async_session)


@pytest.fixture
def sample_tracking():
    """Create sample tracking."""
    return ContentTracking.create(
        tracking_id=TrackingId.generate(),
        user_id="123456789",
        instagram_user_id=InstagramUserId("987654321"),
        instagram_username=InstagramUsername("test_user"),
        content_type=ContentType(ContentTypeEnum.POSTS),
        check_interval=CheckInterval(30),
        notification_enabled=True,
    )


@pytest.mark.asyncio
class TestSQLAlchemyContentTrackingRepository:
    """Test SQLAlchemy content tracking repository."""

    async def test_save_new_tracking(self, repository, sample_tracking):
        """Test saving new tracking."""
        # Act
        await repository.save(sample_tracking)

        # Assert
        found = await repository.find_by_id(sample_tracking.tracking_id)
        assert found is not None
        assert found.tracking_id == sample_tracking.tracking_id
        assert found.user_id == sample_tracking.user_id
        assert found.instagram_username.value == "test_user"

    async def test_save_update_tracking(self, repository, sample_tracking):
        """Test updating existing tracking."""
        # Arrange
        await repository.save(sample_tracking)

        # Act
        sample_tracking.pause()
        await repository.save(sample_tracking)

        # Assert
        found = await repository.find_by_id(sample_tracking.tracking_id)
        assert found.status.is_paused()

    async def test_find_by_id_not_found(self, repository):
        """Test finding non-existent tracking."""
        # Act
        found = await repository.find_by_id(TrackingId.generate())

        # Assert
        assert found is None

    async def test_find_by_user_id(self, repository):
        """Test finding trackings by user ID."""
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
            user_id="user1",
            instagram_user_id=InstagramUserId("ig2"),
            instagram_username=InstagramUsername("ig_user2"),
            content_type=ContentType(ContentTypeEnum.STORIES),
            check_interval=CheckInterval(15),
        )
        tracking3 = ContentTracking.create(
            tracking_id=TrackingId.generate(),
            user_id="user2",
            instagram_user_id=InstagramUserId("ig3"),
            instagram_username=InstagramUsername("ig_user3"),
            content_type=ContentType(ContentTypeEnum.REELS),
            check_interval=CheckInterval(60),
        )

        await repository.save(tracking1)
        await repository.save(tracking2)
        await repository.save(tracking3)

        # Act
        trackings = await repository.find_by_user_id("user1")

        # Assert
        assert len(trackings) == 2
        assert all(t.user_id == "user1" for t in trackings)

    async def test_find_active_trackings(self, repository):
        """Test finding active trackings."""
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
        tracking2.pause()

        await repository.save(tracking1)
        await repository.save(tracking2)

        # Act
        active = await repository.find_active_trackings()

        # Assert
        assert len(active) == 1
        assert active[0].tracking_id == tracking1.tracking_id

    async def test_find_trackings_to_check(self, repository):
        """Test finding trackings to check."""
        # Arrange
        tracking1 = ContentTracking.create(
            tracking_id=TrackingId.generate(),
            user_id="user1",
            instagram_user_id=InstagramUserId("ig1"),
            instagram_username=InstagramUsername("ig_user1"),
            content_type=ContentType(ContentTypeEnum.POSTS),
            check_interval=CheckInterval(30),
        )
        # Set last check to 31 minutes ago
        tracking1.last_check_at = datetime.utcnow() - timedelta(minutes=31)

        tracking2 = ContentTracking.create(
            tracking_id=TrackingId.generate(),
            user_id="user2",
            instagram_user_id=InstagramUserId("ig2"),
            instagram_username=InstagramUsername("ig_user2"),
            content_type=ContentType(ContentTypeEnum.STORIES),
            check_interval=CheckInterval(60),
        )
        # Set last check to 10 minutes ago
        tracking2.last_check_at = datetime.utcnow() - timedelta(minutes=10)

        await repository.save(tracking1)
        await repository.save(tracking2)

        # Act
        to_check = await repository.find_trackings_to_check()

        # Assert
        assert len(to_check) == 1
        assert to_check[0].tracking_id == tracking1.tracking_id

    async def test_delete_tracking(self, repository, sample_tracking):
        """Test deleting tracking."""
        # Arrange
        await repository.save(sample_tracking)

        # Act
        await repository.delete(sample_tracking.tracking_id)

        # Assert
        found = await repository.find_by_id(sample_tracking.tracking_id)
        assert found is None

    async def test_exists(self, repository, sample_tracking):
        """Test checking if tracking exists."""
        # Arrange
        await repository.save(sample_tracking)

        # Act & Assert
        assert await repository.exists(sample_tracking.user_id, sample_tracking.instagram_user_id.value)
        assert not await repository.exists("other_user", sample_tracking.instagram_user_id.value)
        assert not await repository.exists(sample_tracking.user_id, "other_ig_user")

    async def test_exists_ignores_stopped(self, repository, sample_tracking):
        """Test that exists ignores stopped trackings."""
        # Arrange
        await repository.save(sample_tracking)
        sample_tracking.stop()
        await repository.save(sample_tracking)

        # Act & Assert
        assert not await repository.exists(sample_tracking.user_id, sample_tracking.instagram_user_id.value)
