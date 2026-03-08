"""Check Content Updates Use Case."""

from typing import List

from src.application.content_tracking.dtos import ContentUpdateDTO
from src.domain.content_tracking.repositories.content_tracking_repository import IContentTrackingRepository
from src.domain.content_tracking.value_objects.content_type import ContentTypeEnum
from src.infrastructure.external_services.hiker_api.hiker_api_adapter import HikerAPIAdapter


class CheckContentUpdatesUseCase:
    """Use case for checking content updates."""

    def __init__(
        self,
        tracking_repository: IContentTrackingRepository,
        instagram_adapter: HikerAPIAdapter,
    ):
        """Initialize use case.
        
        Args:
            tracking_repository: Content tracking repository
            instagram_adapter: Instagram API adapter
        """
        self.tracking_repository = tracking_repository
        self.instagram_adapter = instagram_adapter

    async def execute(self) -> List[ContentUpdateDTO]:
        """Execute use case - check all trackings for updates.
        
        Returns:
            List of content updates
        """
        updates = []

        # Find trackings that should be checked
        trackings = await self.tracking_repository.find_trackings_to_check()

        for tracking in trackings:
            try:
                # Check for updates based on content type
                if tracking.content_type.is_stories() or tracking.content_type.is_all():
                    story_updates = await self._check_stories(tracking)
                    updates.extend(story_updates)

                if tracking.content_type.is_posts() or tracking.content_type.is_all():
                    post_updates = await self._check_posts(tracking)
                    updates.extend(post_updates)

                if tracking.content_type.is_reels() or tracking.content_type.is_all():
                    reel_updates = await self._check_reels(tracking)
                    updates.extend(reel_updates)

                # Update last check time
                tracking.update_last_check()
                await self.tracking_repository.save(tracking)

            except Exception as e:
                # Log error but continue with other trackings
                print(f"Error checking tracking {tracking.tracking_id.value}: {e}")
                continue

        return updates

    async def _check_stories(self, tracking) -> List[ContentUpdateDTO]:
        """Check for new stories."""
        updates = []

        try:
            stories = await self.instagram_adapter.fetch_stories(tracking.instagram_user_id)

            if stories and len(stories) > 0:
                latest_story = stories[0]
                story_id = latest_story.media_id.value

                # Check if this is a new story
                if tracking.last_content_id != story_id:
                    tracking.detect_new_content(
                        story_id,
                        f"https://instagram.com/stories/{tracking.instagram_username.value}/{story_id}"
                    )

                    updates.append(ContentUpdateDTO(
                        tracking_id=tracking.tracking_id.value,
                        instagram_username=tracking.instagram_username.value,
                        content_type="stories",
                        content_id=story_id,
                        content_url=f"https://instagram.com/stories/{tracking.instagram_username.value}/{story_id}",
                        detected_at=tracking.last_check_at,
                    ))

        except Exception as e:
            print(f"Error checking stories for {tracking.instagram_username.value}: {e}")

        return updates

    async def _check_posts(self, tracking) -> List[ContentUpdateDTO]:
        """Check for new posts."""
        updates = []

        try:
            posts, _ = await self.instagram_adapter.fetch_posts(tracking.instagram_user_id, cursor=None)

            if posts and len(posts) > 0:
                latest_post = posts[0]
                post_id = latest_post.media_id.value

                # Check if this is a new post
                if tracking.last_content_id != post_id:
                    tracking.detect_new_content(
                        post_id,
                        f"https://instagram.com/p/{post_id}"
                    )

                    updates.append(ContentUpdateDTO(
                        tracking_id=tracking.tracking_id.value,
                        instagram_username=tracking.instagram_username.value,
                        content_type="posts",
                        content_id=post_id,
                        content_url=f"https://instagram.com/p/{post_id}",
                        detected_at=tracking.last_check_at,
                    ))

        except Exception as e:
            print(f"Error checking posts for {tracking.instagram_username.value}: {e}")

        return updates

    async def _check_reels(self, tracking) -> List[ContentUpdateDTO]:
        """Check for new reels."""
        updates = []

        try:
            reels, _ = await self.instagram_adapter.fetch_reels(tracking.instagram_user_id, cursor=None)

            if reels and len(reels) > 0:
                latest_reel = reels[0]
                reel_id = latest_reel.media_id.value

                # Check if this is a new reel
                if tracking.last_content_id != reel_id:
                    tracking.detect_new_content(
                        reel_id,
                        f"https://instagram.com/reel/{reel_id}"
                    )

                    updates.append(ContentUpdateDTO(
                        tracking_id=tracking.tracking_id.value,
                        instagram_username=tracking.instagram_username.value,
                        content_type="reels",
                        content_id=reel_id,
                        content_url=f"https://instagram.com/reel/{reel_id}",
                        detected_at=tracking.last_check_at,
                    ))

        except Exception as e:
            print(f"Error checking reels for {tracking.instagram_username.value}: {e}")

        return updates
