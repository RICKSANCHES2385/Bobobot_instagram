"""Tests for StartTrackingUseCase."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.application.content_tracking.use_cases.start_tracking import StartTrackingUseCase
from src.application.content_tracking.dtos import StartTrackingCommand
from src.domain.content_tracking.exceptions import TrackingAlreadyExistsError, TrackingLimitExceededError
from src.domain.instagram_integration.entities.instagram_profile import InstagramProfile
from src.domain.instagram_integration.value_objects.instagram_user_id import InstagramUserId
from src.domain.instagram_integration.value_objects.instagram_username import InstagramUsername
from src.domain.instagram_integration.value_objects.bio import Bio
from src.domain.instagram_integration.value_objects.profile_statistics import ProfileStatistics
from src.domain.instagram_integration.value_objects.media_url import MediaUrl


@pytest.fixture
def mock_tracking_repository():
    """Create mock tracking repository."""
    repo = MagicMock()
    repo.find_by_user_id = AsyncMock(return_value=[])
    repo.exists = AsyncMock(return_value=False)
    repo.save = AsyncMock()
    return repo


@pytest.fixture
def mock_instagram_adapter():
    """Create mock Instagram adapter."""
    adapter = MagicMock()
    adapter.fetch_profile_by_username = AsyncMock()
    return adapter


@pytest.fixture
def sample_profile():
    """Create sample Instagram profile."""
    return InstagramProfile.create(
        user_id=InstagramUserId("123456"),
        username=InstagramUsername("testuser"),
        full_name="Test User",
        bio=Bio("Test bio"),
        statistics=ProfileStatistics(followers=1000, following=500, posts=100),
        is_verified=False,
        is_private=False,
    )


@pytest.mark.asyncio
async def test_start_tracking_success(mock_tracking_repository, mock_instagram_adapter, sample_profile):
    """Test starting tracking successfully."""
    mock_instagram_adapter.fetch_profile_by_username.return_value = sample_profile

    use_case = StartTrackingUseCase(
        tracking_repository=mock_tracking_repository,
        instagram_adapter=mock_instagram_adapter,
        max_trackings_per_user=10,
    )

    command = StartTrackingCommand(
        user_id="user_789",
        instagram_username="testuser",
        content_type="stories",
        check_interval_minutes=30,
    )

    result = await use_case.execute(command)

    assert result.user_id == "user_789"
    assert result.instagram_username == "testuser"
    assert result.content_type == "stories"
    assert result.status == "active"
    mock_tracking_repository.save.assert_called_once()


@pytest.mark.asyncio
async def test_start_tracking_already_exists(mock_tracking_repository, mock_instagram_adapter, sample_profile):
    """Test starting tracking when it already exists."""
    mock_instagram_adapter.fetch_profile_by_username.return_value = sample_profile
    mock_tracking_repository.exists.return_value = True

    use_case = StartTrackingUseCase(
        tracking_repository=mock_tracking_repository,
        instagram_adapter=mock_instagram_adapter,
    )

    command = StartTrackingCommand(
        user_id="user_789",
        instagram_username="testuser",
        content_type="posts",
    )

    with pytest.raises(TrackingAlreadyExistsError):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_start_tracking_limit_exceeded(mock_tracking_repository, mock_instagram_adapter):
    """Test starting tracking when limit exceeded."""
    # Mock 10 existing trackings
    mock_tracking_repository.find_by_user_id.return_value = [MagicMock()] * 10

    use_case = StartTrackingUseCase(
        tracking_repository=mock_tracking_repository,
        instagram_adapter=mock_instagram_adapter,
        max_trackings_per_user=10,
    )

    command = StartTrackingCommand(
        user_id="user_789",
        instagram_username="testuser",
        content_type="reels",
    )

    with pytest.raises(TrackingLimitExceededError):
        await use_case.execute(command)
