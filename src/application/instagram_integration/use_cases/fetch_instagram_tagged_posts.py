"""Fetch Instagram Tagged Posts Use Case."""
from typing import List, Optional
from datetime import datetime

from src.application.shared.use_case import UseCase
from ..dtos import InstagramPostDTO
from src.domain.instagram_integration.entities.post import Post
from src.domain.instagram_integration.value_objects.media_id import MediaId
from src.domain.instagram_integration.value_objects.media_url import MediaUrl
from src.domain.instagram_integration.value_objects.caption import Caption
from src.domain.instagram_integration.value_objects.instagram_user_id import InstagramUserId


class FetchInstagramTaggedPostsCommand:
    """Command for fetching Instagram tagged posts."""
    
    def __init__(self, user_id: str, cursor: Optional[str] = None):
        self.user_id = user_id
        self.cursor = cursor


class FetchInstagramTaggedPostsUseCase(UseCase[FetchInstagramTaggedPostsCommand, List[InstagramPostDTO]]):
    """Use case for fetching Instagram tagged posts."""
    
    def __init__(self, instagram_api_client):
        self.instagram_api_client = instagram_api_client
    
    async def execute(self, command: FetchInstagramTaggedPostsCommand) -> List[InstagramPostDTO]:
        """Execute the use case."""
        tagged_posts, next_cursor = await self.instagram_api_client.get_user_tags_chunk(
            command.user_id,
            command.cursor
        )
        
        post_dtos = []
        for media in tagged_posts:
            try:
                # Determine media type
                media_type_code = media.get("media_type", 1)
                if media_type_code == 2:
                    media_type = "VIDEO"
                elif media_type_code == 8:
                    media_type = "CAROUSEL"
                else:
                    media_type = "IMAGE"
                
                # Get media URLs
                media_urls = []
                if media_type == "VIDEO":
                    url = media.get("video_versions", [{}])[0].get("url")
                    if url:
                        media_urls.append(MediaUrl(value=url))
                else:
                    url = media.get("image_versions2", {}).get("candidates", [{}])[0].get("url")
                    if url:
                        media_urls.append(MediaUrl(value=url))
                
                if not media_urls:
                    continue
                
                post = Post.create(
                    media_id=MediaId(value=str(media.get("pk") or media.get("id", ""))),
                    user_id=InstagramUserId(value=str(media.get("user", {}).get("pk", command.user_id))),
                    media_urls=media_urls,
                    caption=Caption(value=media.get("caption", {}).get("text", "") if isinstance(media.get("caption"), dict) else ""),
                    media_type=media_type,
                    like_count=media.get("like_count", 0),
                    comment_count=media.get("comment_count", 0),
                    taken_at=datetime.fromtimestamp(media.get("taken_at", 0)) if media.get("taken_at") else None
                )
                
                post_dtos.append(InstagramPostDTO(
                    media_id=str(post.media_id),
                    user_id=str(post.user_id),
                    media_urls=[str(url) for url in post.media_urls],
                    caption=str(post.caption),
                    media_type=post.media_type,
                    like_count=post.like_count,
                    comment_count=post.comment_count,
                    taken_at=post.taken_at
                ))
            except Exception:
                continue
        
        return post_dtos
