"""Tests for Instagram Profile Entity."""
import pytest

from src.domain.instagram_integration.entities.instagram_profile import InstagramProfile
from src.domain.instagram_integration.value_objects.instagram_username import InstagramUsername
from src.domain.instagram_integration.value_objects.instagram_user_id import InstagramUserId
from src.domain.instagram_integration.value_objects.bio import Bio
from src.domain.instagram_integration.value_objects.profile_statistics import ProfileStatistics
from src.domain.instagram_integration.value_objects.media_url import MediaUrl


def test_instagram_profile_create():
    """Test Instagram profile creation."""
    # Arrange
    username = InstagramUsername(value="test_user")
    user_id = InstagramUserId(value="123456789")
    full_name = "Test User"
    bio = Bio(value="Test bio")
    statistics = ProfileStatistics(
        followers=1000,
        following=500,
        posts=100
    )
    
    # Act
    profile = InstagramProfile.create(
        username=username,
        user_id=user_id,
        full_name=full_name,
        bio=bio,
        statistics=statistics,
        is_private=False,
        is_verified=True
    )
    
    # Assert
    assert profile.username == username
    assert profile.user_id == user_id
    assert profile.full_name == full_name
    assert profile.bio == bio
    assert profile.statistics == statistics
    assert profile.is_private is False
    assert profile.is_verified is True
    assert profile.profile_pic_url is None
    assert profile.external_url is None


def test_instagram_profile_with_profile_picture():
    """Test Instagram profile with profile picture."""
    # Arrange
    username = InstagramUsername(value="test_user")
    user_id = InstagramUserId(value="123456789")
    bio = Bio(value="Test bio")
    statistics = ProfileStatistics(followers=1000, following=500, posts=100)
    profile_pic_url = MediaUrl(value="https://example.com/pic.jpg")
    
    # Act
    profile = InstagramProfile.create(
        username=username,
        user_id=user_id,
        full_name="Test User",
        bio=bio,
        statistics=statistics,
        profile_pic_url=profile_pic_url
    )
    
    # Assert
    assert profile.has_profile_picture() is True
    assert profile.profile_pic_url == profile_pic_url


def test_instagram_profile_without_profile_picture():
    """Test Instagram profile without profile picture."""
    # Arrange
    username = InstagramUsername(value="test_user")
    user_id = InstagramUserId(value="123456789")
    bio = Bio(value="Test bio")
    statistics = ProfileStatistics(followers=1000, following=500, posts=100)
    
    # Act
    profile = InstagramProfile.create(
        username=username,
        user_id=user_id,
        full_name="Test User",
        bio=bio,
        statistics=statistics
    )
    
    # Assert
    assert profile.has_profile_picture() is False


def test_instagram_profile_with_external_url():
    """Test Instagram profile with external URL."""
    # Arrange
    username = InstagramUsername(value="test_user")
    user_id = InstagramUserId(value="123456789")
    bio = Bio(value="Test bio")
    statistics = ProfileStatistics(followers=1000, following=500, posts=100)
    external_url = "https://example.com"
    
    # Act
    profile = InstagramProfile.create(
        username=username,
        user_id=user_id,
        full_name="Test User",
        bio=bio,
        statistics=statistics,
        external_url=external_url
    )
    
    # Assert
    assert profile.has_external_url() is True
    assert profile.external_url == external_url


def test_instagram_profile_without_external_url():
    """Test Instagram profile without external URL."""
    # Arrange
    username = InstagramUsername(value="test_user")
    user_id = InstagramUserId(value="123456789")
    bio = Bio(value="Test bio")
    statistics = ProfileStatistics(followers=1000, following=500, posts=100)
    
    # Act
    profile = InstagramProfile.create(
        username=username,
        user_id=user_id,
        full_name="Test User",
        bio=bio,
        statistics=statistics
    )
    
    # Assert
    assert profile.has_external_url() is False


def test_instagram_profile_string_representation():
    """Test Instagram profile string representation."""
    # Arrange
    username = InstagramUsername(value="test_user")
    user_id = InstagramUserId(value="123456789")
    full_name = "Test User"
    bio = Bio(value="Test bio")
    statistics = ProfileStatistics(followers=1000, following=500, posts=100)
    
    # Act
    profile = InstagramProfile.create(
        username=username,
        user_id=user_id,
        full_name=full_name,
        bio=bio,
        statistics=statistics
    )
    
    # Assert
    assert str(profile) == "@test_user (Test User)"


def test_instagram_profile_private():
    """Test private Instagram profile."""
    # Arrange
    username = InstagramUsername(value="private_user")
    user_id = InstagramUserId(value="987654321")
    bio = Bio(value="Private account")
    statistics = ProfileStatistics(followers=100, following=50, posts=10)
    
    # Act
    profile = InstagramProfile.create(
        username=username,
        user_id=user_id,
        full_name="Private User",
        bio=bio,
        statistics=statistics,
        is_private=True
    )
    
    # Assert
    assert profile.is_private is True


def test_instagram_profile_verified():
    """Test verified Instagram profile."""
    # Arrange
    username = InstagramUsername(value="verified_user")
    user_id = InstagramUserId(value="111222333")
    bio = Bio(value="Verified account")
    statistics = ProfileStatistics(followers=1000000, following=100, posts=500)
    
    # Act
    profile = InstagramProfile.create(
        username=username,
        user_id=user_id,
        full_name="Verified User",
        bio=bio,
        statistics=statistics,
        is_verified=True
    )
    
    # Assert
    assert profile.is_verified is True
