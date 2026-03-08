"""Tests for Fetch Instagram Profile Use Case."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.application.instagram_integration.use_cases.fetch_instagram_profile import FetchInstagramProfileUseCase
from src.application.instagram_integration.dtos import InstagramProfileDTO
from src.domain.instagram_integration.exceptions import ProfileNotFoundException
from src.domain.instagram_integration.entities.instagram_profile import InstagramProfile
from src.domain.instagram_integration.value_objects.instagram_username import InstagramUsername
from src.domain.instagram_integration.value_objects.instagram_user_id import InstagramUserId
from src.domain.instagram_integration.value_objects.bio import Bio
from src.domain.instagram_integration.value_objects.profile_statistics import ProfileStatistics
from src.domain.instagram_integration.value_objects.media_url import MediaUrl


@pytest.fixture
def mock_api_client():
    """Create mock Instagram API client."""
    return AsyncMock()


@pytest.fixture
def use_case(mock_api_client):
    """Create use case instance."""
    return FetchInstagramProfileUseCase(instagram_api_client=mock_api_client)


def create_mock_profile(
    username="test_user",
    user_id="123456789",
    full_name="Test User",
    bio="Test bio",
    followers=1000,
    following=500,
    posts=100,
    is_private=False,
    is_verified=True,
    profile_pic_url="https://example.com/pic.jpg",
    external_url="https://example.com"
) -> InstagramProfile:
    """Helper to create mock Instagram profile."""
    return InstagramProfile.create(
        username=InstagramUsername(username),
        user_id=InstagramUserId(user_id),
        full_name=full_name,
        bio=Bio(bio),
        statistics=ProfileStatistics(
            followers=followers,
            following=following,
            posts=posts
        ),
        is_private=is_private,
        is_verified=is_verified,
        profile_pic_url=MediaUrl(profile_pic_url) if profile_pic_url else None,
        external_url=external_url
    )


@pytest.mark.asyncio
async def test_fetch_instagram_profile_success(use_case, mock_api_client):
    """Test successful profile fetch."""
    # Arrange
    username = "test_user"
    mock_profile = create_mock_profile()
    mock_api_client.fetch_profile_by_username.return_value = mock_profile
    
    # Act
    result = await use_case.execute(username)
    
    # Assert
    assert isinstance(result, InstagramProfileDTO)
    assert result.username == "test_user"
    assert result.user_id == "123456789"
    assert result.full_name == "Test User"
    assert result.bio == "Test bio"
    assert result.followers == 1000
    assert result.following == 500
    assert result.posts == 100
    assert result.is_private is False
    assert result.is_verified is True
    assert result.profile_pic_url == "https://example.com/pic.jpg"
    assert result.external_url == "https://example.com"
    mock_api_client.fetch_profile_by_username.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_instagram_profile_without_wrapper(use_case, mock_api_client):
    """Test profile fetch without API wrapper."""
    # Arrange
    username = "test_user"
    mock_profile = create_mock_profile(is_verified=False)
    mock_api_client.fetch_profile_by_username.return_value = mock_profile
    
    # Act
    result = await use_case.execute(username)
    
    # Assert
    assert isinstance(result, InstagramProfileDTO)
    assert result.username == "test_user"
    assert result.user_id == "123456789"


@pytest.mark.asyncio
async def test_fetch_instagram_profile_private(use_case, mock_api_client):
    """Test fetching private profile."""
    # Arrange
    username = "private_user"
    mock_profile = create_mock_profile(
        username="private_user",
        user_id="987654321",
        full_name="Private User",
        bio="",
        followers=100,
        following=50,
        posts=10,
        is_private=True,
        is_verified=False,
        profile_pic_url=None,
        external_url=None
    )
    mock_api_client.fetch_profile_by_username.return_value = mock_profile
    
    # Act
    result = await use_case.execute(username)
    
    # Assert
    assert result.is_private is True
    assert result.username == "private_user"


@pytest.mark.asyncio
async def test_fetch_instagram_profile_not_found(use_case, mock_api_client):
    """Test profile not found."""
    # Arrange
    username = "nonexistent_user"
    mock_api_client.fetch_profile_by_username.side_effect = Exception("Profile not found")
    
    # Act & Assert
    with pytest.raises(ProfileNotFoundException):
        await use_case.execute(username)


@pytest.mark.asyncio
async def test_fetch_instagram_profile_without_optional_fields(use_case, mock_api_client):
    """Test profile fetch without optional fields."""
    # Arrange
    username = "minimal_user"
    mock_profile = create_mock_profile(
        username="minimal_user",
        user_id="111222333",
        full_name="Minimal User",
        bio="",
        followers=0,
        following=0,
        posts=0,
        is_private=False,
        is_verified=False,
        profile_pic_url=None,
        external_url=None
    )
    mock_api_client.fetch_profile_by_username.return_value = mock_profile
    
    # Act
    result = await use_case.execute(username)
    
    # Assert
    assert result.username == "minimal_user"
    assert result.profile_pic_url is None
    assert result.external_url is None
    assert result.followers == 0
    assert result.posts == 0
