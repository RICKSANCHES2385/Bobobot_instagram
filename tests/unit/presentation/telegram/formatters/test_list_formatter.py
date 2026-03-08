"""Tests for list formatter."""

from datetime import datetime

from src.presentation.telegram.formatters.list_formatter import (
    format_followers_list,
    format_following_list,
    format_posts_list,
    format_reels_list,
    format_followers_export,
    format_following_export,
)


class TestFormatFollowersList:
    """Tests for format_followers_list function."""

    def test_format_empty_followers(self):
        """Test formatting empty followers list."""
        text = format_followers_list([], "test", 0)
        
        assert "@test" in text
        assert "0" in text

    def test_format_followers_list(self):
        """Test formatting followers list."""
        followers = [
            {"username": "user1", "full_name": "User One", "is_verified": True},
            {"username": "user2", "full_name": "User Two", "is_verified": False},
        ]
        
        text = format_followers_list(followers, "test", 2)
        
        assert "@user1" in text
        assert "User One" in text
        assert "✓" in text
        assert "@user2" in text

    def test_format_many_followers(self):
        """Test formatting many followers (>50)."""
        followers = [{"username": f"user{i}"} for i in range(60)]
        
        text = format_followers_list(followers, "test", 60)
        
        assert "еще 10" in text
        assert "Скачать всех" in text


class TestFormatFollowingList:
    """Tests for format_following_list function."""

    def test_format_following_list(self):
        """Test formatting following list."""
        following = [
            {"username": "user1", "full_name": "User One"},
            {"username": "user2", "full_name": "User Two"},
        ]
        
        text = format_following_list(following, "test", 2)
        
        assert "@user1" in text
        assert "@user2" in text


class TestFormatPostsList:
    """Tests for format_posts_list function."""

    def test_format_posts_list(self):
        """Test formatting posts list."""
        posts = [
            {
                "id": "123",
                "shortcode": "ABC123",
                "caption": "Test post",
                "likes_count": 100,
                "comments_count": 10,
                "created_at": datetime.now(),
            }
        ]
        
        text = format_posts_list(posts, "test")
        
        assert "Post #1" in text
        assert "ABC123" in text
        assert "Test post" in text
        assert "100" in text
        assert "10" in text

    def test_format_empty_posts_list(self):
        """Test formatting empty posts list."""
        text = format_posts_list([], "test")
        
        assert "Total: 0" in text


class TestFormatReelsList:
    """Tests for format_reels_list function."""

    def test_format_reels_list(self):
        """Test formatting reels list."""
        reels = [
            {
                "id": "123",
                "shortcode": "ABC123",
                "caption": "Test reel",
                "views_count": 1000,
                "likes_count": 100,
                "duration_seconds": 30,
                "created_at": datetime.now(),
            }
        ]
        
        text = format_reels_list(reels, "test")
        
        assert "Reel #1" in text
        assert "ABC123" in text
        assert "Test reel" in text
        assert "1000" in text
        assert "0:30" in text


class TestFormatFollowersExport:
    """Tests for format_followers_export function."""

    def test_format_followers_export(self):
        """Test formatting followers for export."""
        followers = [
            {"username": "user1", "full_name": "User One", "is_verified": True, "is_private": False},
            {"username": "user2", "full_name": "User Two", "is_verified": False, "is_private": True},
        ]
        
        text = format_followers_export(followers, "test")
        
        assert "@user1" in text
        assert "User One" in text
        assert "Verified" in text
        assert "@user2" in text
        assert "Private" in text


class TestFormatFollowingExport:
    """Tests for format_following_export function."""

    def test_format_following_export(self):
        """Test formatting following for export."""
        following = [
            {"username": "user1", "full_name": "User One", "is_verified": True},
            {"username": "user2", "full_name": "User Two", "is_verified": False},
        ]
        
        text = format_following_export(following, "test")
        
        assert "@user1" in text
        assert "User One" in text
        assert "Verified" in text
        assert "@user2" in text
