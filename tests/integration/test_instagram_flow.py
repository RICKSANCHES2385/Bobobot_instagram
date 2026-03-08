"""Integration tests for Instagram flow."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.presentation.telegram.handlers.instagram_handlers import (
    parse_instagram_username,
    send_user_profile,
    instagram_profile_handler,
    handle_stories,
    handle_posts,
    handle_reels,
    handle_highlights,
    handle_followers,
    handle_following,
)
from src.application.instagram_integration.dtos import (
    InstagramProfileDTO,
    InstagramStoryDTO,
    InstagramPostDTO,
    InstagramReelDTO,
    InstagramHighlightDTO,
    FollowersListDTO,
    FollowingListDTO,
)


class TestParseInstagramUsername:
    """Test Instagram username parsing."""
    
    def test_parse_plain_username(self):
        """Test parsing plain username."""
        assert parse_instagram_username("cristiano") == "cristiano"
    
    def test_parse_username_with_at(self):
        """Test parsing username with @ prefix."""
        assert parse_instagram_username("@cristiano") == "cristiano"
    
    def test_parse_instagram_url(self):
        """Test parsing Instagram URL."""
        assert parse_instagram_username("https://instagram.com/cristiano") == "cristiano"
        assert parse_instagram_username("https://www.instagram.com/cristiano/") == "cristiano"
    
    def test_parse_instagr_am_url(self):
        """Test parsing instagr.am URL."""
        assert parse_instagram_username("https://instagr.am/cristiano") == "cristiano"
    
    def test_parse_invalid_username(self):
        """Test parsing invalid username."""
        assert parse_instagram_username("invalid username!") is None
        assert parse_instagram_username("") is None


@pytest.mark.asyncio
class TestInstagramProfileFlow:
    """Test Instagram profile viewing flow."""
    
    async def test_send_user_profile_success(self):
        """Test successful profile sending."""
        # Mock message
        message = AsyncMock()
        message.answer = AsyncMock()
        
        # Mock profile DTO
        profile = InstagramProfileDTO(
            user_id="123",
            username="testuser",
            full_name="Test User",
            bio="Test bio",
            profile_pic_url="https://example.com/pic.jpg",
            is_private=False,
            is_verified=False,
            followers=1000,
            following=500,
            posts=100,
        )
        
        # Mock Use Case
        with patch("src.presentation.telegram.handlers.instagram_handlers.get_container") as mock_container:
            mock_use_cases = MagicMock()
            # Правильно настраиваем мок - execute должен возвращать профиль
            mock_fetch_profile = AsyncMock()
            mock_fetch_profile.execute = AsyncMock(return_value=profile)
            mock_use_cases.fetch_instagram_profile = mock_fetch_profile
            mock_use_cases.get_user_trackings = AsyncMock()
            mock_use_cases.get_user_trackings.execute = AsyncMock(return_value=[])
            mock_container.return_value.get_use_cases.return_value = mock_use_cases
            
            await send_user_profile(message, "testuser", "123")
            
            # Verify message was sent
            message.answer.assert_called_once()
            call_args = message.answer.call_args
            assert "testuser" in call_args[0][0]
            assert "1K" in call_args[0][0] or "1.0K" in call_args[0][0]  # Formatted follower count
    
    async def test_send_user_profile_error(self):
        """Test profile sending with error."""
        # Mock message
        message = AsyncMock()
        message.answer = AsyncMock()
        
        # Mock Use Case to raise error
        with patch("src.presentation.telegram.handlers.instagram_handlers.get_container") as mock_container:
            mock_use_cases = MagicMock()
            mock_fetch_profile = AsyncMock()
            mock_fetch_profile.execute = AsyncMock(side_effect=Exception("API Error"))
            mock_use_cases.fetch_instagram_profile = mock_fetch_profile
            mock_container.return_value.get_use_cases.return_value = mock_use_cases
            
            await send_user_profile(message, "testuser", "123")
            
            # Verify error message was sent
            message.answer.assert_called_once()
            call_args = message.answer.call_args
            assert "Не удалось получить профиль" in call_args[0][0]


@pytest.mark.asyncio
class TestInstagramContentFlow:
    """Test Instagram content loading flow."""
    
    async def test_handle_stories_success(self):
        """Test successful stories loading."""
        # Mock callback
        callback = AsyncMock()
        callback.data = "ig_stories_123_testuser"
        callback.from_user = MagicMock(id=123)
        callback.message = AsyncMock()
        callback.message.answer = AsyncMock()
        callback.message.bot = AsyncMock()
        callback.answer = AsyncMock()
        
        # Mock profile
        from src.application.instagram_integration.dtos import InstagramProfileDTO
        profile = InstagramProfileDTO(
            user_id="456",
            username="testuser",
            full_name="Test User",
            bio="Test bio",
            profile_pic_url="https://example.com/pic.jpg",
            is_private=False,
            is_verified=False,
            followers=1000,
            following=500,
            posts=100,
        )
        
        # Mock stories
        stories = [
            InstagramStoryDTO(
                media_id="story1",
                user_id="123",
                media_type="photo",
                media_url="https://example.com/story1.jpg",
                taken_at=datetime.now(),
            ),
            InstagramStoryDTO(
                media_id="story2",
                user_id="123",
                media_type="video",
                media_url="https://example.com/story2.mp4",
                taken_at=datetime.now(),
            ),
        ]
        
        # Mock Use Case
        with patch("src.presentation.telegram.handlers.instagram_handlers.get_container") as mock_container:
            mock_use_cases = MagicMock()
            mock_fetch_profile = AsyncMock()
            mock_fetch_profile.execute = AsyncMock(return_value=profile)
            mock_use_cases.fetch_instagram_profile = mock_fetch_profile
            
            mock_fetch_stories = AsyncMock()
            mock_fetch_stories.execute = AsyncMock(return_value=stories)
            mock_use_cases.fetch_instagram_stories = mock_fetch_stories
            
            mock_container.return_value.get_use_cases.return_value = mock_use_cases
            
            # Mock media handlers
            with patch("src.presentation.telegram.handlers.instagram_handlers.MediaDownloader") as mock_downloader_class:
                with patch("src.presentation.telegram.handlers.instagram_handlers.MediaSender") as mock_sender_class:
                    mock_downloader = AsyncMock()
                    mock_downloader.download_media = AsyncMock(return_value="/tmp/story.jpg")
                    mock_downloader_class.return_value = mock_downloader
                    
                    mock_sender = AsyncMock()
                    mock_sender.send_media = AsyncMock()
                    mock_sender_class.return_value = mock_sender
                    
                    await handle_stories(callback)
            
            # Verify callback was answered
            callback.answer.assert_called_once()
            
            # Verify stories were sent
            assert callback.message.answer.call_count >= 1
    
    async def test_handle_stories_empty(self):
        """Test stories loading with no stories."""
        # Mock callback
        callback = AsyncMock()
        callback.data = "ig_stories_123_testuser"
        callback.from_user = MagicMock(id=123)
        callback.message = AsyncMock()
        callback.message.answer = AsyncMock()
        callback.message.bot = AsyncMock()
        callback.answer = AsyncMock()
        
        # Mock profile
        from src.application.instagram_integration.dtos import InstagramProfileDTO
        profile = InstagramProfileDTO(
            user_id="456",
            username="testuser",
            full_name="Test User",
            bio="Test bio",
            profile_pic_url="https://example.com/pic.jpg",
            is_private=False,
            is_verified=False,
            followers=1000,
            following=500,
            posts=100,
        )
        
        # Mock Use Case to return empty list
        with patch("src.presentation.telegram.handlers.instagram_handlers.get_container") as mock_container:
            mock_use_cases = MagicMock()
            mock_fetch_profile = AsyncMock()
            mock_fetch_profile.execute = AsyncMock(return_value=profile)
            mock_use_cases.fetch_instagram_profile = mock_fetch_profile
            
            mock_fetch_stories = AsyncMock()
            mock_fetch_stories.execute = AsyncMock(return_value=[])
            mock_use_cases.fetch_instagram_stories = mock_fetch_stories
            
            mock_container.return_value.get_use_cases.return_value = mock_use_cases
            
            await handle_stories(callback)
            
            # Verify message about no stories
            callback.message.answer.assert_called_once()
            call_args = callback.message.answer.call_args
            assert "нет активных историй" in call_args[0][0]


@pytest.mark.asyncio
class TestInstagramSocialFlow:
    """Test Instagram social features flow."""
    
    async def test_handle_followers_success(self):
        """Test successful followers loading."""
        # Mock callback
        callback = AsyncMock()
        callback.data = "ig_followers_123_testuser"
        callback.from_user = MagicMock(id=123)
        callback.message = AsyncMock()
        callback.message.answer = AsyncMock()
        callback.answer = AsyncMock()
        
        # Mock profile
        from src.application.instagram_integration.dtos import InstagramProfileDTO
        profile = InstagramProfileDTO(
            user_id="456",
            username="testuser",
            full_name="Test User",
            bio="Test bio",
            profile_pic_url="https://example.com/pic.jpg",
            is_private=False,
            is_verified=False,
            followers=1000,
            following=500,
            posts=100,
        )
        
        # Mock followers
        from src.application.instagram_integration.dtos import FollowerDTO
        followers_dto = FollowersListDTO(
            username="testuser",
            user_id="123",
            followers=[
                FollowerDTO(user_id="1", username="follower1", full_name="Follower One"),
                FollowerDTO(user_id="2", username="follower2", full_name="Follower Two"),
            ],
            total_count=100,
        )
        
        # Mock Use Case
        with patch("src.presentation.telegram.handlers.instagram_handlers.get_container") as mock_container:
            mock_use_cases = MagicMock()
            mock_fetch_profile = AsyncMock()
            mock_fetch_profile.execute = AsyncMock(return_value=profile)
            mock_use_cases.fetch_instagram_profile = mock_fetch_profile
            
            mock_fetch_followers = AsyncMock()
            mock_fetch_followers.execute = AsyncMock(return_value=followers_dto)
            mock_use_cases.fetch_instagram_followers = mock_fetch_followers
            
            mock_container.return_value.get_use_cases.return_value = mock_use_cases
            
            await handle_followers(callback)
            
            # Verify callback was answered
            callback.answer.assert_called_once()
            
            # Verify followers list was sent
            callback.message.answer.assert_called_once()
            call_args = callback.message.answer.call_args
            assert "follower1" in call_args[0][0]
            assert "follower2" in call_args[0][0]
