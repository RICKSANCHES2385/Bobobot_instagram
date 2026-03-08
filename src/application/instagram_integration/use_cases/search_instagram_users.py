"""Search Instagram Users Use Case."""
from typing import List

from src.application.shared.use_case import UseCase
from ..dtos import InstagramProfileDTO
from src.domain.instagram_integration.entities.instagram_profile import InstagramProfile
from src.domain.instagram_integration.value_objects.instagram_username import InstagramUsername
from src.domain.instagram_integration.value_objects.instagram_user_id import InstagramUserId
from src.domain.instagram_integration.value_objects.bio import Bio
from src.domain.instagram_integration.value_objects.profile_statistics import ProfileStatistics
from src.domain.instagram_integration.value_objects.media_url import MediaUrl


class SearchInstagramUsersUseCase(UseCase[str, List[InstagramProfileDTO]]):
    """Use case for searching Instagram users."""
    
    def __init__(self, instagram_api_client):
        self.instagram_api_client = instagram_api_client
    
    async def execute(self, query: str) -> List[InstagramProfileDTO]:
        """Execute the use case."""
        search_results = await self.instagram_api_client.search_users(query)
        
        # Extract users from response
        if isinstance(search_results, dict):
            users = search_results.get("users", [])
        else:
            users = search_results if isinstance(search_results, list) else []
        
        profile_dtos = []
        for user_data in users:
            try:
                # Get user object if nested
                if "user" in user_data:
                    user_data = user_data["user"]
                
                profile_pic_url_value = user_data.get("profile_pic_url")
                
                profile = InstagramProfile.create(
                    username=InstagramUsername(value=user_data.get("username", "")),
                    user_id=InstagramUserId(value=str(user_data.get("pk") or user_data.get("id", ""))),
                    full_name=user_data.get("full_name", ""),
                    bio=Bio(value=""),  # Search results don't include bio
                    statistics=ProfileStatistics(
                        followers=user_data.get("follower_count", 0),
                        following=0,  # Not included in search
                        posts=0  # Not included in search
                    ),
                    is_private=user_data.get("is_private", False),
                    is_verified=user_data.get("is_verified", False),
                    profile_pic_url=MediaUrl(value=profile_pic_url_value) if profile_pic_url_value else None
                )
                
                profile_dtos.append(InstagramProfileDTO(
                    username=str(profile.username),
                    user_id=str(profile.user_id),
                    full_name=profile.full_name,
                    bio=str(profile.bio),
                    followers=profile.statistics.followers,
                    following=profile.statistics.following,
                    posts=profile.statistics.posts,
                    is_private=profile.is_private,
                    is_verified=profile.is_verified,
                    profile_pic_url=str(profile.profile_pic_url) if profile.profile_pic_url else None,
                    external_url=profile.external_url
                ))
            except Exception:
                continue
        
        return profile_dtos
