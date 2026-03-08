"""Tests for HikerAPIAdapter."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.domain.instagram_integration.value_objects.instagram_user_id import InstagramUserId
from src.domain.instagram_integration.value_objects.instagram_username import InstagramUsername
from src.infrastructure.external_services.hiker_api.hiker_api_adapter import HikerAPIAdapter


@pytest.fixture
def adapter():
    """Create HikerAPIAdapter instance."""
    return HikerAPIAdapter(api_key="test_key", base_url="https://api.test.com")


@pytest.fixture
def mock_client():
    """Create mock HTTP client."""
    client = MagicMock()
    client.request = AsyncMock()
    client.aclose = AsyncMock()
    return client


class TestHikerAPIAdapter:
    """Test HikerAPIAdapter."""

    @pytest.mark.asyncio
    async def test_fetch_profile_by_username(self, adapter, mock_client):
        """Test fetching profile by username."""
        adapter.client = mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "pk": "123456",
            "username": "testuser",
            "full_name": "Test User",
            "biography": "Test bio",
            "profile_pic_url": "https://example.com/pic.jpg",
            "is_verified": True,
            "is_private": False,
            "follower_count": 1000,
            "following_count": 500,
            "media_count": 100,
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.request.return_value = mock_response

        username = InstagramUsername("testuser")
        profile = await adapter.fetch_profile_by_username(username)

        assert profile.user_id.value == "123456"
        assert profile.username.value == "testuser"
        assert profile.full_name == "Test User"
        assert profile.is_verified is True
        mock_client.request.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_stories(self, adapter, mock_client):
        """Test fetching stories."""
        adapter.client = mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "reel": {
                "items": [
                    {
                        "pk": "story1",
                        "user": {"pk": "123456"},
                        "video_versions": [{"url": "https://example.com/video.mp4"}],
                        "image_versions2": {"candidates": [{"url": "https://example.com/thumb.jpg"}]},
                        "taken_at": 1234567890,
                        "expiring_at": 1234654290,
                    }
                ]
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.request.return_value = mock_response

        user_id = InstagramUserId("123456")
        stories = await adapter.fetch_stories(user_id)

        assert len(stories) == 1
        assert stories[0].media_id.value == "story1"
        assert stories[0].user_id.value == "123456"

    @pytest.mark.asyncio
    async def test_fetch_posts_with_pagination(self, adapter, mock_client):
        """Test fetching posts with pagination."""
        adapter.client = mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "pk": "post1",
                    "user": {"pk": "123456"},
                    "caption": {"text": "Test post"},
                    "image_versions2": {"candidates": [{"url": "https://example.com/img.jpg"}]},
                    "like_count": 100,
                    "comment_count": 10,
                    "taken_at": 1234567890,
                }
            ],
            "next_max_id": "cursor123",
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.request.return_value = mock_response

        user_id = InstagramUserId("123456")
        posts, next_cursor = await adapter.fetch_posts(user_id)

        assert len(posts) == 1
        assert posts[0].media_id.value == "post1"
        assert next_cursor == "cursor123"

    @pytest.mark.asyncio
    async def test_fetch_reels(self, adapter, mock_client):
        """Test fetching reels."""
        adapter.client = mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "pk": "reel1",
                    "user": {"pk": "123456"},
                    "caption": {"text": "Test reel"},
                    "video_versions": [{"url": "https://example.com/video.mp4"}],
                    "image_versions2": {"candidates": [{"url": "https://example.com/thumb.jpg"}]},
                    "view_count": 5000,
                    "like_count": 200,
                    "comment_count": 20,
                    "taken_at": 1234567890,
                }
            ],
            "next_cursor": None,
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.request.return_value = mock_response

        user_id = InstagramUserId("123456")
        reels, next_cursor = await adapter.fetch_reels(user_id)

        assert len(reels) == 1
        assert reels[0].media_id.value == "reel1"
        assert reels[0].play_count == 5000
        assert next_cursor is None

    @pytest.mark.asyncio
    async def test_fetch_highlights(self, adapter, mock_client):
        """Test fetching highlights."""
        adapter.client = mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "id": "highlight1",
                "user": {"pk": "123456"},
                "title": "Travel",
                "cover_media": {"cropped_image_version": {"url": "https://example.com/cover.jpg"}},
            }
        ]
        mock_response.raise_for_status = MagicMock()
        mock_client.request.return_value = mock_response

        user_id = InstagramUserId("123456")
        highlights = await adapter.fetch_highlights(user_id)

        assert len(highlights) == 1
        assert highlights[0].highlight_id.value == "highlight1"
        assert highlights[0].title.value == "Travel"

    @pytest.mark.asyncio
    async def test_fetch_followers(self, adapter, mock_client):
        """Test fetching followers."""
        adapter.client = mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "users": [
                {
                    "pk": "follower1",
                    "username": "follower_user",
                    "full_name": "Follower User",
                    "profile_pic_url": "https://example.com/pic.jpg",
                    "is_verified": False,
                    "is_private": False,
                    "follower_count": 100,
                    "following_count": 50,
                    "media_count": 10,
                }
            ],
            "next_cursor": "cursor456",
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.request.return_value = mock_response

        user_id = InstagramUserId("123456")
        followers, next_cursor = await adapter.fetch_followers(user_id)

        assert len(followers) == 1
        assert followers[0].username.value == "follower_user"
        assert next_cursor == "cursor456"

    @pytest.mark.asyncio
    async def test_search_users(self, adapter, mock_client):
        """Test searching users."""
        adapter.client = mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "users": [
                {
                    "user": {
                        "pk": "search1",
                        "username": "search_user",
                        "full_name": "Search User",
                        "profile_pic_url": "https://example.com/pic.jpg",
                        "is_verified": True,
                        "follower_count": 10000,
                    }
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.request.return_value = mock_response

        results = await adapter.search_users("test query")

        assert len(results) == 1
        assert results[0].username.value == "search_user"
        assert results[0].is_verified is True

    @pytest.mark.asyncio
    async def test_close(self, adapter, mock_client):
        """Test closing adapter."""
        adapter.client = mock_client
        await adapter.close()
        mock_client.aclose.assert_called_once()

    def test_extract_list_response_dict(self, adapter):
        """Test extracting list from dict response."""
        result = {"items": [{"id": 1}], "next_max_id": "cursor"}
        items, cursor = adapter._extract_list_response(result, "items")
        assert len(items) == 1
        assert cursor == "cursor"

    def test_extract_list_response_list_tuple(self, adapter):
        """Test extracting list from tuple response."""
        result = [[{"id": 1}], "cursor"]
        items, cursor = adapter._extract_list_response(result, "items")
        assert len(items) == 1
        assert cursor == "cursor"

    def test_extract_list_response_simple_list(self, adapter):
        """Test extracting simple list response."""
        result = [{"id": 1}, {"id": 2}]
        items, cursor = adapter._extract_list_response(result, "items")
        assert len(items) == 2
        assert cursor is None
