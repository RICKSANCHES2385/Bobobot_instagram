"""Fetch Instagram Comments Use Case."""
from typing import List, Optional
from datetime import datetime

from src.application.shared.use_case import UseCase
from ..dtos import InstagramCommentDTO
from src.domain.instagram_integration.entities.comment import Comment
from src.domain.instagram_integration.value_objects.comment_id import CommentId
from src.domain.instagram_integration.value_objects.comment_text import CommentText
from src.domain.instagram_integration.value_objects.instagram_user_id import InstagramUserId
from src.domain.instagram_integration.value_objects.instagram_username import InstagramUsername
from src.domain.instagram_integration.value_objects.media_id import MediaId


class FetchInstagramCommentsCommand:
    """Command for fetching Instagram comments."""
    
    def __init__(self, media_id: str, cursor: Optional[str] = None):
        self.media_id = media_id
        self.cursor = cursor


class FetchInstagramCommentsUseCase(UseCase[FetchInstagramCommentsCommand, List[InstagramCommentDTO]]):
    """Use case for fetching Instagram comments."""
    
    def __init__(self, instagram_api_client):
        self.instagram_api_client = instagram_api_client
    
    async def execute(self, command: FetchInstagramCommentsCommand) -> List[InstagramCommentDTO]:
        """Execute the use case."""
        comments, next_cursor = await self.instagram_api_client.get_media_comments_chunk(
            command.media_id,
            command.cursor
        )
        
        comment_dtos = []
        for comment_data in comments:
            try:
                comment = Comment.create(
                    comment_id=CommentId(value=str(comment_data.get("pk") or comment_data.get("id", ""))),
                    media_id=MediaId(value=command.media_id),
                    user_id=InstagramUserId(value=str(comment_data.get("user", {}).get("pk", ""))),
                    username=InstagramUsername(value=comment_data.get("user", {}).get("username", "")),
                    text=CommentText(value=comment_data.get("text", "")),
                    like_count=comment_data.get("comment_like_count", 0),
                    created_at=datetime.fromtimestamp(comment_data.get("created_at", 0)) if comment_data.get("created_at") else None
                )
                
                comment_dtos.append(InstagramCommentDTO(
                    comment_id=str(comment.comment_id),
                    media_id=str(comment.media_id),
                    user_id=str(comment.user_id),
                    username=str(comment.username),
                    text=str(comment.text),
                    like_count=comment.like_count,
                    created_at=comment.created_at
                ))
            except Exception:
                continue
        
        return comment_dtos
