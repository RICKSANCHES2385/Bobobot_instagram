"""Fetch Instagram Highlights Use Case."""
from typing import List

from src.application.shared.use_case import UseCase
from ..dtos import InstagramHighlightDTO
from src.domain.instagram_integration.entities.highlight import Highlight
from src.domain.instagram_integration.value_objects.highlight_id import HighlightId
from src.domain.instagram_integration.value_objects.highlight_title import HighlightTitle
from src.domain.instagram_integration.value_objects.media_url import MediaUrl
from src.domain.instagram_integration.value_objects.instagram_user_id import InstagramUserId


class FetchInstagramHighlightsUseCase(UseCase[str, List[InstagramHighlightDTO]]):
    """Use case for fetching Instagram highlights."""
    
    def __init__(self, instagram_api_client):
        self.instagram_api_client = instagram_api_client
    
    async def execute(self, user_id: str) -> List[InstagramHighlightDTO]:
        """Execute the use case."""
        highlights_data = await self.instagram_api_client.get_user_highlights(user_id, amount=50)
        
        # Extract highlights from response
        if isinstance(highlights_data, dict):
            response_data = highlights_data.get("response", {})
            highlights = response_data.get("items", []) or response_data.get("tray", [])
        else:
            highlights = highlights_data if isinstance(highlights_data, list) else []
        
        highlight_dtos = []
        for hl in highlights:
            try:
                cover_url = hl.get("cover_media", {}).get("cropped_image_version", {}).get("url")
                if not cover_url:
                    continue
                
                highlight = Highlight.create(
                    highlight_id=HighlightId(value=str(hl.get("id") or hl.get("pk", ""))),
                    user_id=InstagramUserId(value=user_id),
                    title=HighlightTitle(value=hl.get("title", "")),
                    cover_url=MediaUrl(value=cover_url),
                    story_count=hl.get("media_count", 0)
                )
                
                highlight_dtos.append(InstagramHighlightDTO(
                    highlight_id=str(highlight.highlight_id),
                    user_id=str(highlight.user_id),
                    title=str(highlight.title),
                    cover_url=str(highlight.cover_url),
                    story_count=highlight.story_count
                ))
            except Exception:
                continue
        
        return highlight_dtos
