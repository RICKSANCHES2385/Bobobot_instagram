"""Fetch Instagram Reels Use Case."""
from typing import List, Optional
from datetime import datetime

from src.application.shared.use_case import UseCase
from ..dtos import InstagramReelDTO
from src.domain.instagram_integration.entities.reel import Reel
from src.domain.instagram_integration.value_objects.media_id import MediaId
from src.domain.instagram_integration.value_objects.media_url import MediaUrl
from src.domain.instagram_integration.value_objects.caption import Caption
from src.domain.instagram_integration.value_objects.instagram_user_id import InstagramUserId


class FetchInstagramReelsCommand:
    """Command for fetching Instagram reels."""
    
    def __init__(self, user_id: str, cursor: Optional[str] = None):
        self.user_id = user_id
        self.cursor = cursor


class FetchInstagramReelsUseCase(UseCase[FetchInstagramReelsCommand, List[InstagramReelDTO]]):
    """Use case for fetching Instagram reels."""
    
    def __init__(self, instagram_api_client):
        self.instagram_api_client = instagram_api_client
    
    async def execute(self, command: FetchInstagramReelsCommand) -> List[InstagramReelDTO]:
        """Execute the use case."""
        clips, next_cursor = await self.instagram_api_client.get_user_clips_chunk(
            command.user_id,
            command.cursor
        )
        
        reel_dtos = []
        for clip in clips:
            try:
                video_url = clip.get("video_versions", [{}])[0].get("url")
                if not video_url:
                    continue
                
                thumbnail_url_value = clip.get("image_versions2", {}).get("candidates", [{}])[0].get("url")
                
                reel = Reel.create(
                    media_id=MediaId(value=str(clip.get("pk") or clip.get("id", ""))),
                    user_id=InstagramUserId(value=command.user_id),
                    video_url=MediaUrl(value=video_url),
                    caption=Caption(value=clip.get("caption", {}).get("text", "") if isinstance(clip.get("caption"), dict) else ""),
                    thumbnail_url=MediaUrl(value=thumbnail_url_value) if thumbnail_url_value else None,
                    like_count=clip.get("like_count", 0),
                    comment_count=clip.get("comment_count", 0),
                    play_count=clip.get("play_count", 0),
                    taken_at=datetime.fromtimestamp(clip.get("taken_at", 0)) if clip.get("taken_at") else None
                )
                
                reel_dtos.append(InstagramReelDTO(
                    media_id=str(reel.media_id),
                    user_id=str(reel.user_id),
                    video_url=str(reel.video_url),
                    caption=str(reel.caption),
                    thumbnail_url=str(reel.thumbnail_url) if reel.thumbnail_url else None,
                    like_count=reel.like_count,
                    comment_count=reel.comment_count,
                    play_count=reel.play_count,
                    taken_at=reel.taken_at
                ))
            except Exception:
                continue
        
        return reel_dtos
