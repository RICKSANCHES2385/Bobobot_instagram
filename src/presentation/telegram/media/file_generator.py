"""File generator for exporting data."""

from typing import List
from datetime import datetime

from src.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class FileGenerator:
    """Generate text files for data export."""
    
    @staticmethod
    def generate_followers_file(followers: List[dict], username: str) -> bytes:
        """Generate followers list as txt file.
        
        Args:
            followers: List of follower dicts with 'username' and 'full_name'
            username: Instagram username
            
        Returns:
            File content as bytes
        """
        lines = [
            f"Подписчики @{username}",
            f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            f"Всего: {len(followers)}",
            "",
            "=" * 50,
            ""
        ]
        
        for idx, follower in enumerate(followers, 1):
            follower_username = follower.get("username", "unknown")
            full_name = follower.get("full_name", "")
            
            if full_name:
                lines.append(f"{idx}. @{follower_username} ({full_name})")
            else:
                lines.append(f"{idx}. @{follower_username}")
        
        content = "\n".join(lines)
        return content.encode("utf-8")
    
    @staticmethod
    def generate_following_file(following: List[dict], username: str) -> bytes:
        """Generate following list as txt file.
        
        Args:
            following: List of following dicts with 'username' and 'full_name'
            username: Instagram username
            
        Returns:
            File content as bytes
        """
        lines = [
            f"Подписки @{username}",
            f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            f"Всего: {len(following)}",
            "",
            "=" * 50,
            ""
        ]
        
        for idx, user in enumerate(following, 1):
            user_username = user.get("username", "unknown")
            full_name = user.get("full_name", "")
            
            if full_name:
                lines.append(f"{idx}. @{user_username} ({full_name})")
            else:
                lines.append(f"{idx}. @{user_username}")
        
        content = "\n".join(lines)
        return content.encode("utf-8")
    
    @staticmethod
    def generate_posts_file(posts: List[dict], username: str) -> bytes:
        """Generate posts list as txt file.
        
        Args:
            posts: List of post dicts with 'id', 'caption', 'created_at'
            username: Instagram username
            
        Returns:
            File content as bytes
        """
        lines = [
            f"Публикации @{username}",
            f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            f"Всего: {len(posts)}",
            "",
            "=" * 50,
            ""
        ]
        
        for idx, post in enumerate(posts, 1):
            post_id = post.get("id", "unknown")
            caption = post.get("caption", "")
            created_at = post.get("created_at", "")
            
            lines.append(f"{idx}. Post ID: {post_id}")
            if created_at:
                lines.append(f"   Дата: {created_at}")
            if caption:
                # Truncate long captions
                caption_preview = caption[:100] + "..." if len(caption) > 100 else caption
                lines.append(f"   Текст: {caption_preview}")
            lines.append(f"   URL: https://instagram.com/p/{post_id}")
            lines.append("")
        
        content = "\n".join(lines)
        return content.encode("utf-8")
    
    @staticmethod
    def generate_reels_file(reels: List[dict], username: str) -> bytes:
        """Generate reels list as txt file.
        
        Args:
            reels: List of reel dicts with 'id', 'caption', 'created_at'
            username: Instagram username
            
        Returns:
            File content as bytes
        """
        lines = [
            f"Reels @{username}",
            f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            f"Всего: {len(reels)}",
            "",
            "=" * 50,
            ""
        ]
        
        for idx, reel in enumerate(reels, 1):
            reel_id = reel.get("id", "unknown")
            caption = reel.get("caption", "")
            created_at = reel.get("created_at", "")
            
            lines.append(f"{idx}. Reel ID: {reel_id}")
            if created_at:
                lines.append(f"   Дата: {created_at}")
            if caption:
                # Truncate long captions
                caption_preview = caption[:100] + "..." if len(caption) > 100 else caption
                lines.append(f"   Текст: {caption_preview}")
            lines.append(f"   URL: https://instagram.com/reel/{reel_id}")
            lines.append("")
        
        content = "\n".join(lines)
        return content.encode("utf-8")
