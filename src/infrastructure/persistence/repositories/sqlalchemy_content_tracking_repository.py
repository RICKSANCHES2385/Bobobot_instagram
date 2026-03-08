"""SQLAlchemy Content Tracking Repository."""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.content_tracking.repositories.content_tracking_repository import IContentTrackingRepository
from src.domain.content_tracking.aggregates.content_tracking import ContentTracking
from src.domain.content_tracking.value_objects.tracking_id import TrackingId
from src.domain.content_tracking.value_objects.tracking_status import TrackingStatus, TrackingStatusEnum
from src.domain.content_tracking.value_objects.content_type import ContentType, ContentTypeEnum
from src.domain.content_tracking.value_objects.check_interval import CheckInterval
from src.domain.instagram_integration.value_objects.instagram_user_id import InstagramUserId
from src.domain.instagram_integration.value_objects.instagram_username import InstagramUsername
from src.infrastructure.persistence.models.content_tracking_model import (
    ContentTrackingModel,
    TrackingStatusDB,
    ContentTypeDB,
)


class SQLAlchemyContentTrackingRepository(IContentTrackingRepository):
    """SQLAlchemy implementation of content tracking repository."""

    def __init__(self, session: AsyncSession):
        """Initialize repository.
        
        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    async def save(self, tracking: ContentTracking) -> None:
        """Save content tracking."""
        model = await self._session.get(ContentTrackingModel, tracking.tracking_id.value)

        if model is None:
            # Create new
            model = self._to_model(tracking)
            self._session.add(model)
        else:
            # Update existing
            self._update_model(model, tracking)

        await self._session.flush()

    async def find_by_id(self, tracking_id: TrackingId) -> Optional[ContentTracking]:
        """Find content tracking by ID."""
        model = await self._session.get(ContentTrackingModel, tracking_id.value)
        return self._to_entity(model) if model else None

    async def find_by_user_id(self, user_id: str) -> List[ContentTracking]:
        """Find all trackings for a user."""
        stmt = select(ContentTrackingModel).where(
            ContentTrackingModel.user_id == user_id
        ).order_by(ContentTrackingModel.created_at.desc())

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def find_active_trackings(self) -> List[ContentTracking]:
        """Find all active trackings."""
        stmt = select(ContentTrackingModel).where(
            ContentTrackingModel.status == TrackingStatusDB.ACTIVE
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def find_trackings_to_check(self) -> List[ContentTracking]:
        """Find trackings that should be checked now."""
        # Get all active trackings
        trackings = await self.find_active_trackings()

        # Filter by should_check_now
        return [t for t in trackings if t.should_check_now()]

    async def delete(self, tracking_id: TrackingId) -> None:
        """Delete content tracking."""
        model = await self._session.get(ContentTrackingModel, tracking_id.value)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def exists(self, user_id: str, instagram_user_id: str) -> bool:
        """Check if tracking exists for user and Instagram profile."""
        stmt = select(ContentTrackingModel).where(
            and_(
                ContentTrackingModel.user_id == user_id,
                ContentTrackingModel.instagram_user_id == instagram_user_id,
                ContentTrackingModel.status != TrackingStatusDB.STOPPED,
            )
        )

        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    def _to_model(self, tracking: ContentTracking) -> ContentTrackingModel:
        """Convert entity to model."""
        return ContentTrackingModel(
            id=tracking.tracking_id.value,
            user_id=tracking.user_id,
            instagram_user_id=tracking.instagram_user_id.value,
            instagram_username=tracking.instagram_username.value,
            content_type=self._map_content_type_to_db(tracking.content_type),
            status=self._map_status_to_db(tracking.status),
            check_interval_minutes=tracking.check_interval.minutes,
            last_check_at=tracking.last_check_at,
            last_content_id=tracking.last_content_id,
            notification_enabled=tracking.notification_enabled,
            created_at=tracking.created_at,
            updated_at=tracking.updated_at,
        )

    def _update_model(self, model: ContentTrackingModel, tracking: ContentTracking) -> None:
        """Update model from entity."""
        model.status = self._map_status_to_db(tracking.status)
        model.check_interval_minutes = tracking.check_interval.minutes
        model.last_check_at = tracking.last_check_at
        model.last_content_id = tracking.last_content_id
        model.notification_enabled = tracking.notification_enabled
        model.updated_at = tracking.updated_at

    def _to_entity(self, model: ContentTrackingModel) -> ContentTracking:
        """Convert model to entity."""
        tracking = ContentTracking(
            id=model.id,
            tracking_id=TrackingId(model.id),
            user_id=model.user_id,
            instagram_user_id=InstagramUserId(model.instagram_user_id),
            instagram_username=InstagramUsername(model.instagram_username),
            content_type=self._map_content_type_from_db(model.content_type),
            status=self._map_status_from_db(model.status),
            check_interval=CheckInterval(model.check_interval_minutes),
            last_check_at=model.last_check_at,
            last_content_id=model.last_content_id,
            notification_enabled=model.notification_enabled,
        )
        tracking.created_at = model.created_at
        tracking.updated_at = model.updated_at
        return tracking

    @staticmethod
    def _map_status_to_db(status: TrackingStatus) -> TrackingStatusDB:
        """Map domain status to database enum."""
        mapping = {
            TrackingStatusEnum.ACTIVE: TrackingStatusDB.ACTIVE,
            TrackingStatusEnum.PAUSED: TrackingStatusDB.PAUSED,
            TrackingStatusEnum.STOPPED: TrackingStatusDB.STOPPED,
        }
        return mapping[status.value]

    @staticmethod
    def _map_status_from_db(status: TrackingStatusDB) -> TrackingStatus:
        """Map database enum to domain status."""
        mapping = {
            TrackingStatusDB.ACTIVE: TrackingStatusEnum.ACTIVE,
            TrackingStatusDB.PAUSED: TrackingStatusEnum.PAUSED,
            TrackingStatusDB.STOPPED: TrackingStatusEnum.STOPPED,
        }
        return TrackingStatus(mapping[status])

    @staticmethod
    def _map_content_type_to_db(content_type: ContentType) -> ContentTypeDB:
        """Map domain content type to database enum."""
        mapping = {
            ContentTypeEnum.POSTS: ContentTypeDB.POSTS,
            ContentTypeEnum.STORIES: ContentTypeDB.STORIES,
            ContentTypeEnum.REELS: ContentTypeDB.REELS,
            ContentTypeEnum.ALL: ContentTypeDB.HIGHLIGHTS,  # Map ALL to HIGHLIGHTS for backward compatibility
        }
        return mapping[content_type.value]

    @staticmethod
    def _map_content_type_from_db(content_type: ContentTypeDB) -> ContentType:
        """Map database enum to domain content type."""
        mapping = {
            ContentTypeDB.POSTS: ContentTypeEnum.POSTS,
            ContentTypeDB.STORIES: ContentTypeEnum.STORIES,
            ContentTypeDB.REELS: ContentTypeEnum.REELS,
            ContentTypeDB.HIGHLIGHTS: ContentTypeEnum.ALL,  # Map HIGHLIGHTS to ALL for backward compatibility
        }
        return ContentType(mapping[content_type])
