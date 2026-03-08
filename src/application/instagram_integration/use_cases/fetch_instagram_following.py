"""Fetch Instagram Following Use Case."""
from typing import Optional

from src.application.shared.use_case import UseCase
from ..dtos import FollowingListDTO, FollowerDTO


class FetchInstagramFollowingCommand:
    """Command for fetching Instagram following."""
    
    def __init__(self, username: str, user_id: str, cursor: Optional[str] = None):
        self.username = username
        self.user_id = user_id
        self.cursor = cursor


class FetchInstagramFollowingUseCase(UseCase[FetchInstagramFollowingCommand, FollowingListDTO]):
    """Use case for fetching Instagram following."""
    
    def __init__(self, instagram_api_client):
        self.instagram_api_client = instagram_api_client
    
    async def execute(self, command: FetchInstagramFollowingCommand) -> FollowingListDTO:
        """Execute the use case."""
        following, next_cursor = await self.instagram_api_client.get_user_following_chunk(
            command.user_id,
            command.cursor
        )
        
        following_dtos = []
        for user in following:
            try:
                following_dtos.append(FollowerDTO(
                    user_id=str(user.get("pk") or user.get("id", "")),
                    username=user.get("username", ""),
                    full_name=user.get("full_name", ""),
                    profile_pic_url=user.get("profile_pic_url"),
                    is_verified=user.get("is_verified", False)
                ))
            except Exception:
                continue
        
        return FollowingListDTO(
            username=command.username,
            user_id=command.user_id,
            following=following_dtos,
            total_count=len(following_dtos),
            has_more=next_cursor is not None
        )
