"""HikerAPI Adapter for Instagram Integration."""

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from src.domain.instagram_integration.entities.comment import Comment
from src.domain.instagram_integration.entities.highlight import Highlight
from src.domain.instagram_integration.entities.instagram_profile import InstagramProfile
from src.domain.instagram_integration.entities.post import Post
from src.domain.instagram_integration.entities.reel import Reel
from src.domain.instagram_integration.entities.story import Story
from src.domain.instagram_integration.entities.user_search_result import UserSearchResult
from src.domain.instagram_integration.value_objects.instagram_user_id import InstagramUserId
from src.domain.instagram_integration.value_objects.instagram_username import InstagramUsername
from src.domain.instagram_integration.value_objects.media_url import MediaUrl


class HikerAPIAdapter:
    """Adapter for HikerAPI Instagram API."""

    def __init__(self, api_key: str, base_url: str = "https://api.hikerapi.com") -> None:
        """Initialize HikerAPI adapter.
        
        Args:
            api_key: HikerAPI access key
            base_url: HikerAPI base URL
        """
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"x-access-key": self.api_key},
            timeout=30.0,
        )

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """Make HTTP request with retry logic."""
        response = await self.client.request(method, endpoint, **kwargs)
        response.raise_for_status()
        data = response.json()
        return data if data is not None else {}

    async def fetch_profile_by_username(self, username: InstagramUsername) -> InstagramProfile:
        """Fetch Instagram profile by username."""
        data = await self._request("GET", "/v2/user/by/username", params={"username": username.value})
        return self._map_to_profile(data)

    async def fetch_profile_by_id(self, user_id: InstagramUserId) -> InstagramProfile:
        """Fetch Instagram profile by user ID."""
        data = await self._request("GET", "/v2/user/by/id", params={"id": user_id.value})
        return self._map_to_profile(data)

    async def fetch_stories(self, user_id: InstagramUserId) -> list[Story]:
        """Fetch user stories."""
        data = await self._request("GET", "/v2/user/stories", params={"user_id": user_id.value})
        items = data.get("reel", {}).get("items", [])
        return [self._map_to_story(item) for item in items]

    async def fetch_posts(self, user_id: InstagramUserId, cursor: str | None = None) -> tuple[list[Post], str | None]:
        """Fetch user posts with pagination."""
        params = {"user_id": user_id.value}
        if cursor:
            params["end_cursor"] = cursor
        result = await self._request("GET", "/v1/user/medias/chunk", params=params)
        
        medias, next_cursor = self._extract_list_response(result, "items")
        posts = [self._map_to_post(item) for item in medias]
        return posts, next_cursor

    async def fetch_reels(self, user_id: InstagramUserId, cursor: str | None = None) -> tuple[list[Reel], str | None]:
        """Fetch user reels with pagination."""
        params = {"user_id": user_id.value}
        if cursor:
            params["end_cursor"] = cursor
        result = await self._request("GET", "/v1/user/clips/chunk", params=params)
        
        clips, next_cursor = self._extract_list_response(result, "items")
        reels = [self._map_to_reel(item) for item in clips]
        return reels, next_cursor

    async def fetch_highlights(self, user_id: InstagramUserId) -> list[Highlight]:
        """Fetch user highlights."""
        data = await self._request("GET", "/v2/user/highlights", params={"user_id": user_id.value, "amount": 20})
        highlights = data if isinstance(data, list) else []
        return [self._map_to_highlight(item) for item in highlights]

    async def fetch_highlight_stories(self, highlight_id: str) -> list[Story]:
        """Fetch stories from a highlight."""
        data = await self._request("GET", "/v2/highlight/by/id", params={"id": highlight_id})
        items = data.get("items", [])
        return [self._map_to_story(item) for item in items]

    async def fetch_followers(self, user_id: InstagramUserId, cursor: str | None = None) -> tuple[list[InstagramProfile], str | None]:
        """Fetch user followers with pagination."""
        params = {"user_id": user_id.value}
        if cursor:
            params["end_cursor"] = cursor
        result = await self._request("GET", "/gql/user/followers/chunk", params=params)
        
        users, next_cursor = self._extract_list_response(result, "users", "items")
        profiles = [self._map_to_profile(item) for item in users]
        return profiles, next_cursor

    async def fetch_following(self, user_id: InstagramUserId, cursor: str | None = None) -> tuple[list[InstagramProfile], str | None]:
        """Fetch user following with pagination."""
        params = {"user_id": user_id.value}
        if cursor:
            params["end_cursor"] = cursor
        result = await self._request("GET", "/gql/user/following/chunk", params=params)
        
        users, next_cursor = self._extract_list_response(result, "users", "items")
        profiles = [self._map_to_profile(item) for item in users]
        return profiles, next_cursor

    async def fetch_comments(self, media_id: str, cursor: str | None = None) -> tuple[list[Comment], str | None]:
        """Fetch media comments with pagination."""
        params = {"media_id": media_id}
        if cursor:
            params["end_cursor"] = cursor
        result = await self._request("GET", "/gql/comments/chunk", params=params)
        
        comments_data, next_cursor = self._extract_list_response(result, "comments", "items")
        comments = [self._map_to_comment(item) for item in comments_data]
        return comments, next_cursor

    async def fetch_tagged_posts(self, user_id: InstagramUserId, cursor: str | None = None) -> tuple[list[Post], str | None]:
        """Fetch user tagged posts with pagination."""
        params = {"user_id": user_id.value}
        if cursor:
            params["end_cursor"] = cursor
        result = await self._request("GET", "/v1/user/tag/medias/chunk", params=params)
        
        medias, next_cursor = self._extract_list_response(result, "items")
        posts = [self._map_to_post(item) for item in medias]
        return posts, next_cursor

    async def search_users(self, query: str) -> list[UserSearchResult]:
        """Search users by query."""
        data = await self._request("GET", "/gql/topsearch", params={"query": query, "flat": True})
        users = data.get("users", []) if isinstance(data, dict) else []
        return [self._map_to_search_result(item) for item in users]

    def _extract_list_response(self, result: Any, *keys: str) -> tuple[list[dict[str, Any]], str | None]:
        """Extract list and cursor from API response."""
        if isinstance(result, dict):
            items = None
            for key in keys:
                items = result.get(key)
                if items:
                    break
            items = items or []
            next_cursor = result.get("next_max_id") or result.get("next_cursor")
            return items, next_cursor
        elif isinstance(result, list) and len(result) >= 2 and isinstance(result[0], list):
            return result[0], result[1]
        elif isinstance(result, list):
            return result, None
        return [], None

    def _map_to_profile(self, data: dict[str, Any]) -> InstagramProfile:
        """Map API data to InstagramProfile entity."""
        from src.domain.instagram_integration.value_objects.bio import Bio
        from src.domain.instagram_integration.value_objects.profile_statistics import ProfileStatistics
        
        return InstagramProfile.create(
            user_id=InstagramUserId(str(data.get("pk") or data.get("id"))),
            username=InstagramUsername(data.get("username", "")),
            full_name=data.get("full_name", ""),
            bio=Bio(data.get("biography", "")),
            statistics=ProfileStatistics(
                followers=data.get("follower_count", 0),
                following=data.get("following_count", 0),
                posts=data.get("media_count", 0),
            ),
            is_verified=data.get("is_verified", False),
            is_private=data.get("is_private", False),
            profile_pic_url=MediaUrl(data.get("profile_pic_url", "")) if data.get("profile_pic_url") else None,
            external_url=data.get("external_url"),
        )

    def _map_to_story(self, data: dict[str, Any]) -> Story:
        """Map API data to Story entity."""
        from src.domain.instagram_integration.value_objects.media_id import MediaId
        from datetime import datetime
        
        media_type = "VIDEO" if "video_versions" in data else "IMAGE"
        taken_at = datetime.fromtimestamp(data.get("taken_at", 0)) if data.get("taken_at") else None
        expires_at = datetime.fromtimestamp(data.get("expiring_at", 0)) if data.get("expiring_at") else None
        
        return Story.create(
            media_id=MediaId(str(data.get("pk") or data.get("id"))),
            user_id=InstagramUserId(str(data.get("user", {}).get("pk", ""))),
            media_url=MediaUrl(self._extract_media_url(data)),
            media_type=media_type,
            taken_at=taken_at,
            expires_at=expires_at,
        )

    def _map_to_post(self, data: dict[str, Any]) -> Post:
        """Map API data to Post entity."""
        from src.domain.instagram_integration.value_objects.media_id import MediaId
        from src.domain.instagram_integration.value_objects.caption import Caption
        from datetime import datetime
        
        caption_text = data.get("caption", {}).get("text", "") if isinstance(data.get("caption"), dict) else ""
        media_type = "VIDEO" if "video_versions" in data else "IMAGE"
        taken_at = datetime.fromtimestamp(data.get("taken_at", 0)) if data.get("taken_at") else None
        
        media_url = self._extract_media_url(data)
        media_urls = [MediaUrl(media_url)] if media_url else []
        
        return Post.create(
            media_id=MediaId(str(data.get("pk") or data.get("id"))),
            user_id=InstagramUserId(str(data.get("user", {}).get("pk", ""))),
            media_urls=media_urls,
            caption=Caption(caption_text),
            media_type=media_type,
            like_count=data.get("like_count", 0),
            comment_count=data.get("comment_count", 0),
            taken_at=taken_at,
        )

    def _map_to_reel(self, data: dict[str, Any]) -> Reel:
        """Map API data to Reel entity."""
        from src.domain.instagram_integration.value_objects.media_id import MediaId
        from src.domain.instagram_integration.value_objects.caption import Caption
        from datetime import datetime
        
        caption_text = data.get("caption", {}).get("text", "") if isinstance(data.get("caption"), dict) else ""
        taken_at = datetime.fromtimestamp(data.get("taken_at", 0)) if data.get("taken_at") else None
        thumbnail = data.get("image_versions2", {}).get("candidates", [{}])[0].get("url", "")
        
        return Reel.create(
            media_id=MediaId(str(data.get("pk") or data.get("id"))),
            user_id=InstagramUserId(str(data.get("user", {}).get("pk", ""))),
            video_url=MediaUrl(self._extract_video_url(data)),
            caption=Caption(caption_text),
            thumbnail_url=MediaUrl(thumbnail) if thumbnail else None,
            like_count=data.get("like_count", 0),
            comment_count=data.get("comment_count", 0),
            play_count=data.get("view_count", 0) or data.get("play_count", 0),
            taken_at=taken_at,
        )

    def _map_to_highlight(self, data: dict[str, Any]) -> Highlight:
        """Map API data to Highlight entity."""
        from src.domain.instagram_integration.value_objects.highlight_id import HighlightId
        from src.domain.instagram_integration.value_objects.highlight_title import HighlightTitle
        
        return Highlight.create(
            highlight_id=HighlightId(str(data.get("id"))),
            user_id=InstagramUserId(str(data.get("user", {}).get("pk", ""))),
            title=HighlightTitle(data.get("title", "")),
            cover_url=MediaUrl(data.get("cover_media", {}).get("cropped_image_version", {}).get("url", "")),
            story_count=data.get("media_count", 0),
        )

    def _map_to_comment(self, data: dict[str, Any]) -> Comment:
        """Map API data to Comment entity."""
        return Comment.create(
            comment_id=str(data.get("pk") or data.get("id")),
            user_id=InstagramUserId(str(data.get("user", {}).get("pk", ""))),
            username=InstagramUsername(data.get("user", {}).get("username", "")),
            text=data.get("text", ""),
            created_at=data.get("created_at", 0),
        )

    def _map_to_search_result(self, data: dict[str, Any]) -> UserSearchResult:
        """Map API data to UserSearchResult entity."""
        user_data = data.get("user", data)
        return UserSearchResult.create(
            user_id=InstagramUserId(str(user_data.get("pk") or user_data.get("id"))),
            username=InstagramUsername(user_data.get("username", "")),
            full_name=user_data.get("full_name", ""),
            profile_pic_url=MediaUrl(user_data.get("profile_pic_url", "")),
            is_verified=user_data.get("is_verified", False),
            follower_count=user_data.get("follower_count", 0),
        )

    def _extract_media_url(self, data: dict[str, Any]) -> str:
        """Extract media URL from API data."""
        if "video_versions" in data:
            return data["video_versions"][0].get("url", "")
        if "image_versions2" in data:
            return data["image_versions2"].get("candidates", [{}])[0].get("url", "")
        return ""

    def _extract_video_url(self, data: dict[str, Any]) -> str:
        """Extract video URL from API data."""
        if "video_versions" in data:
            return data["video_versions"][0].get("url", "")
        return ""
