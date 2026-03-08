"""Media downloader for Instagram content."""

import asyncio
from typing import Optional
from pathlib import Path
import httpx

from src.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class MediaDownloader:
    """Download media from Instagram URLs."""
    
    def __init__(self, timeout: int = 30):
        """Initialize downloader."""
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout, follow_redirects=True)
    
    async def download_image(self, url: str) -> Optional[bytes]:
        """Download image from URL.
        
        Args:
            url: Image URL
            
        Returns:
            Image bytes or None if failed
        """
        try:
            logger.debug(f"Downloading image from {url}")
            response = await self.client.get(url)
            response.raise_for_status()
            
            content_type = response.headers.get("content-type", "")
            if not content_type.startswith("image/"):
                logger.warning(f"Invalid content type: {content_type}")
                return None
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error downloading image from {url}: {e}")
            return None
    
    async def download_video(self, url: str) -> Optional[bytes]:
        """Download video from URL.
        
        Args:
            url: Video URL
            
        Returns:
            Video bytes or None if failed
        """
        try:
            logger.debug(f"Downloading video from {url}")
            response = await self.client.get(url)
            response.raise_for_status()
            
            content_type = response.headers.get("content-type", "")
            if not content_type.startswith("video/"):
                logger.warning(f"Invalid content type: {content_type}")
                return None
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error downloading video from {url}: {e}")
            return None
    
    async def download_multiple(self, urls: list[str], media_type: str = "image") -> list[Optional[bytes]]:
        """Download multiple media files concurrently.
        
        Args:
            urls: List of media URLs
            media_type: Type of media ("image" or "video")
            
        Returns:
            List of media bytes (None for failed downloads)
        """
        if media_type == "image":
            tasks = [self.download_image(url) for url in urls]
        else:
            tasks = [self.download_video(url) for url in urls]
        
        return await asyncio.gather(*tasks, return_exceptions=False)
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
