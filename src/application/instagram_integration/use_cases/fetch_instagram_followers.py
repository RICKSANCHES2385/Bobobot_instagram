"""Fetch Instagram Followers Use Case."""
from typing import Optional

from src.application.shared.use_case import UseCase
from ..dtos import FollowersListDTO, FollowerDTO


class FetchInstagramFollowersCommand:
    """Command for fetching Instagram followers."""
    
    def __init__(self, username: str, user_id: str, cursor: Optional[str] = None):
        self.username = username
        self.user_id = user_id
        self.cursor = cursor


class FetchInstagramFollowersUseCase(UseCase[FetchInstagramFollowersCommand, FollowersListDTO]):
    """Use case for fetching Instagram followers."""
    
    def __init__(self, instagram_api_client):
        self.instagram_api_client = instagram_api_client
    
    async def execute(self, command: FetchInstagramFollowersCommand) -> FollowersListDTO:
        """Execute the use case."""
        followers, next_cursor = await self.instagram_api_client.get_user_followers_chunk(
            command.user_id,
            command.cursor
        )
        
        follower_dtos = []
        for follower in followers:
            try:
                follower_dtos.append(FollowerDTO(
                    user_id=str(follower.get("pk") or follower.get("id", "")),
                    username=follower.get("username", ""),
                    full_name=follower.get("full_name", ""),
                    profile_pic_url=follower.get("profile_pic_url"),
                    is_verified=follower.get("is_verified", False)
                ))
            except Exception:
                continue
        
        return FollowersListDTO(
            username=command.username,
            user_id=command.user_id,
            followers=follower_dtos,
            total_count=len(follower_dtos),
            has_more=next_cursor is not None
        )
