"""Fetch Instagram Highlight Stories Use Case."""
from typing import List
from datetime import datetime

from src.application.shared.use_case import UseCase
from ..dtos import InstagramStoryDTO
from src.domain.instagram_integration.entities.story import Story
from src.domain.instagram_integration.value_objects.media_id import MediaId
from src.domain.instagram_integration.value_objects.media_url import MediaUrl
from src.domain.instagram_integration.value_objects.instagram_user_id import InstagramUserId


class FetchInstagramHighlightStoriesUseCase(UseCase[str, List[InstagramStoryDTO]]):
    """Use case for fetching Instagram highlight stories."""
    
    def __init__(self, instagram_api_client):
        self.instagram_api_client = instagram_api_client
    
    async def execute(self, highlight_id: str) -> List[InstagramStoryDTO]:
        """Execute the use case."""
        highlight_data = await self.instagram_api_client.get_highlight_by_id(highlight_id)
        
        # Extract items from response
        if isinstance(highlight_data, dict):
            items = highlight_data.get("items", []) or highlight_data.get("reel", {}).get("items", [])
            user_id = highlight_data.get("user", {}).get("pk", "") or highlight_data.get("reel", {}).get("user", {}).get("pk", "")
        else:
            items = []
            user_id = ""
        
        story_dtos = []
        for item in items:
            try:
                media_type = "VIDEO" if item.get("media_type") == 2 else "IMAGE"
                
                if media_type == "VIDEO":
                    media_url_value = item.get("video_versions", [{}])[0].get("url")
                else:
                    media_url_value = item.get("image_versions2", {}).get("candidates", [{}])[0].get("url")
                
                if not media_url_value:
                    continue
                
                story = Story.create(
                    media_id=MediaId(value=str(item.get("pk") or item.get("id", ""))),
                    user_id=InstagramUserId(value=str(user_id)),
                    media_url=MediaUrl(value=media_url_value),
                    media_type=media_type,
                    taken_at=datetime.fromtimestamp(item.get("taken_at", 0)) if item.get("taken_at") else None
                )
                
                story_dtos.append(InstagramStoryDTO(
                    media_id=str(story.media_id),
                    user_id=str(story.user_id),
                    media_url=str(story.media_url),
                    media_type=story.media_type,
                    taken_at=story.taken_at,
                    expires_at=None
                ))
            except Exception:
                continue
        
        return story_dtos
