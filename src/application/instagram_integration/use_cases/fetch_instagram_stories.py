"""Fetch Instagram Stories Use Case."""
from typing import List
from datetime import datetime

from src.application.shared.use_case import UseCase
from ..dtos import InstagramStoryDTO
from src.domain.instagram_integration.entities.story import Story
from src.domain.instagram_integration.value_objects.media_id import MediaId
from src.domain.instagram_integration.value_objects.media_url import MediaUrl
from src.domain.instagram_integration.value_objects.instagram_user_id import InstagramUserId
from src.domain.instagram_integration.exceptions import ProfileNotFoundException


class FetchInstagramStoriesCommand:
    """Command for fetching Instagram stories."""
    
    def __init__(self, username: str, user_id: str):
        self.username = username
        self.user_id = user_id


class FetchInstagramStoriesUseCase(UseCase[FetchInstagramStoriesCommand, List[InstagramStoryDTO]]):
    """Use case for fetching Instagram stories.
    
    This use case fetches active Instagram stories for a user.
    """
    
    def __init__(self, instagram_api_client):
        """Initialize use case.
        
        Args:
            instagram_api_client: Client for Instagram API (HikerAPI)
        """
        self.instagram_api_client = instagram_api_client
    
    async def execute(self, command: FetchInstagramStoriesCommand) -> List[InstagramStoryDTO]:
        """Execute the use case.
        
        Args:
            command: Command with username and user_id
            
        Returns:
            List of InstagramStoryDTO
            
        Raises:
            ProfileNotFoundException: If profile is not found
        """
        # Fetch stories from API
        try:
            stories_data = await self.instagram_api_client.get_user_stories(command.user_id)
        except Exception as e:
            raise ProfileNotFoundException(command.username) from e
        
        # Handle wrapped response
        if isinstance(stories_data, dict):
            items = stories_data.get('items', []) or stories_data.get('reel', {}).get('items', [])
        else:
            items = stories_data if isinstance(stories_data, list) else []
        
        # Convert to domain entities and DTOs
        story_dtos = []
        for item in items:
            try:
                # Create domain entity
                media_type = "VIDEO" if item.get("media_type") == 2 else "IMAGE"
                
                # Get media URL
                if media_type == "VIDEO":
                    media_url_value = item.get("video_versions", [{}])[0].get("url") if item.get("video_versions") else None
                else:
                    media_url_value = item.get("image_versions2", {}).get("candidates", [{}])[0].get("url") if item.get("image_versions2") else None
                
                if not media_url_value:
                    continue
                
                story = Story.create(
                    media_id=MediaId(value=str(item.get("pk") or item.get("id", ""))),
                    user_id=InstagramUserId(value=command.user_id),
                    media_url=MediaUrl(value=media_url_value),
                    media_type=media_type,
                    taken_at=datetime.fromtimestamp(item.get("taken_at", 0)) if item.get("taken_at") else None,
                    expires_at=datetime.fromtimestamp(item.get("expiring_at", 0)) if item.get("expiring_at") else None
                )
                
                # Convert to DTO
                story_dtos.append(InstagramStoryDTO(
                    media_id=str(story.media_id),
                    user_id=str(story.user_id),
                    media_url=str(story.media_url),
                    media_type=story.media_type,
                    taken_at=story.taken_at,
                    expires_at=story.expires_at
                ))
            except Exception:
                # Skip invalid stories
                continue
        
        return story_dtos
