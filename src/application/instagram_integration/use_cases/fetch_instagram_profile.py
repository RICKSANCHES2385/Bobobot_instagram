"""Fetch Instagram Profile Use Case."""
from src.application.shared.use_case import UseCase
from ..dtos import InstagramProfileDTO
from src.domain.instagram_integration.entities.instagram_profile import InstagramProfile
from src.domain.instagram_integration.value_objects.instagram_username import InstagramUsername
from src.domain.instagram_integration.value_objects.instagram_user_id import InstagramUserId
from src.domain.instagram_integration.value_objects.bio import Bio
from src.domain.instagram_integration.value_objects.profile_statistics import ProfileStatistics
from src.domain.instagram_integration.value_objects.media_url import MediaUrl
from src.domain.instagram_integration.exceptions import ProfileNotFoundException


class FetchInstagramProfileUseCase(UseCase[str, InstagramProfileDTO]):
    """Use case for fetching Instagram profile data.
    
    This use case fetches Instagram profile information by username.
    It returns profile data including statistics, bio, and verification status.
    """
    
    def __init__(self, instagram_api_client):
        """Initialize use case.
        
        Args:
            instagram_api_client: Client for Instagram API (HikerAPI)
        """
        self.instagram_api_client = instagram_api_client
    
    async def execute(self, username: str) -> InstagramProfileDTO:
        """Execute the use case.
        
        Args:
            username: Instagram username to fetch
            
        Returns:
            InstagramProfileDTO with profile data
            
        Raises:
            ProfileNotFoundException: If profile is not found
        """
        # Fetch profile data from API
        try:
            instagram_username = InstagramUsername(username)
            profile = await self.instagram_api_client.fetch_profile_by_username(instagram_username)
        except Exception as e:
            raise ProfileNotFoundException(username) from e
        
        # Convert domain entity to DTO
        return self._to_dto(profile)
    
    def _to_dto(self, profile: InstagramProfile) -> InstagramProfileDTO:
        """Convert domain entity to DTO.
        
        Args:
            profile: Instagram profile entity
            
        Returns:
            InstagramProfileDTO
        """
        return InstagramProfileDTO(
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
        )
