"""Media sender for Telegram bot."""

from typing import Optional, List
from io import BytesIO

from aiogram import Bot
from aiogram.types import InputMediaPhoto, InputMediaVideo, BufferedInputFile, Message

from src.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class MediaSender:
    """Send media to Telegram users."""
    
    def __init__(self, bot: Bot):
        """Initialize sender."""
        self.bot = bot
    
    async def send_photo(
        self,
        chat_id: int,
        photo: bytes,
        caption: Optional[str] = None,
        filename: str = "photo.jpg"
    ) -> Optional[Message]:
        """Send photo to user.
        
        Args:
            chat_id: User chat ID
            photo: Photo bytes
            caption: Optional caption
            filename: Filename for photo
            
        Returns:
            Sent message or None if failed
        """
        try:
            photo_file = BufferedInputFile(photo, filename=filename)
            return await self.bot.send_photo(
                chat_id=chat_id,
                photo=photo_file,
                caption=caption,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Error sending photo to {chat_id}: {e}")
            return None
    
    async def send_video(
        self,
        chat_id: int,
        video: bytes,
        caption: Optional[str] = None,
        filename: str = "video.mp4",
        duration: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> Optional[Message]:
        """Send video to user.
        
        Args:
            chat_id: User chat ID
            video: Video bytes
            caption: Optional caption
            filename: Filename for video
            duration: Video duration in seconds
            width: Video width
            height: Video height
            
        Returns:
            Sent message or None if failed
        """
        try:
            video_file = BufferedInputFile(video, filename=filename)
            return await self.bot.send_video(
                chat_id=chat_id,
                video=video_file,
                caption=caption,
                parse_mode="HTML",
                duration=duration,
                width=width,
                height=height
            )
        except Exception as e:
            logger.error(f"Error sending video to {chat_id}: {e}")
            return None
    
    async def send_media_group(
        self,
        chat_id: int,
        media_list: List[tuple[bytes, str, str]],  # (bytes, type, caption)
        caption: Optional[str] = None
    ) -> Optional[List[Message]]:
        """Send media group (album) to user.
        
        Args:
            chat_id: User chat ID
            media_list: List of (media_bytes, media_type, caption) tuples
            caption: Optional caption for first media
            
        Returns:
            List of sent messages or None if failed
        """
        try:
            media_group = []
            
            for idx, (media_bytes, media_type, item_caption) in enumerate(media_list):
                # Use main caption for first item, item caption for others
                current_caption = caption if idx == 0 and caption else item_caption
                
                if media_type == "photo":
                    photo_file = BufferedInputFile(media_bytes, filename=f"photo_{idx}.jpg")
                    media_group.append(
                        InputMediaPhoto(
                            media=photo_file,
                            caption=current_caption,
                            parse_mode="HTML"
                        )
                    )
                elif media_type == "video":
                    video_file = BufferedInputFile(media_bytes, filename=f"video_{idx}.mp4")
                    media_group.append(
                        InputMediaVideo(
                            media=video_file,
                            caption=current_caption,
                            parse_mode="HTML"
                        )
                    )
            
            if not media_group:
                return None
            
            return await self.bot.send_media_group(
                chat_id=chat_id,
                media=media_group
            )
            
        except Exception as e:
            logger.error(f"Error sending media group to {chat_id}: {e}")
            return None
    
    async def send_document(
        self,
        chat_id: int,
        document: bytes,
        filename: str,
        caption: Optional[str] = None
    ) -> Optional[Message]:
        """Send document to user.
        
        Args:
            chat_id: User chat ID
            document: Document bytes
            filename: Filename
            caption: Optional caption
            
        Returns:
            Sent message or None if failed
        """
        try:
            doc_file = BufferedInputFile(document, filename=filename)
            return await self.bot.send_document(
                chat_id=chat_id,
                document=doc_file,
                caption=caption,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Error sending document to {chat_id}: {e}")
            return None
