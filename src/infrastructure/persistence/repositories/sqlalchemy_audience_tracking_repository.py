"""SQLAlchemy Audience Tracking Repository Implementation."""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.audience_tracking.aggregates.audience_tracking import AudienceTracking
from src.domain.audience_tracking.repositories.audience_tracking_repository import (
    AudienceTrackingRepository,
)
from src.domain.audience_tracking.value_objects.tracking_id import TrackingId
from src.domain.audience_tracking.value_objects.follower_count import FollowerCount
from src.domain.audience_tracking.value_objects.following_count import FollowingCount
from src.infrastructure.persistence.models.audience_tracking_model import AudienceTrackingModel
from src.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class SqlAlchemyAudienceTrackingRepository(AudienceTrackingRepository):
    """SQLAlchemy implementation of audience tracking repository."""

    def __init__(self, session: AsyncSession):
        """Initialize repository.
        
        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def save(self, tracking: AudienceTracking) -> AudienceTracking:
        """Save audience tracking subscription."""
        if tracking.id is None:
            # Create new
            model = self._to_model(tracking)
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)
            
            # Update aggregate with generated ID
            tracking.id = str(model.id)
            tracking.tracking_id = TrackingId(model.id)
            tracking.created_at = model.created_at
            tracking.updated_at = model.updated_at
            
            logger.info(f"Created audience tracking {model.id}")
        else:
            # Update existing
            stmt = select(AudienceTrackingModel).where(
                AudienceTrackingModel.id == int(tracking.id)
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model:
                self._update_model(model, tracking)
                await self.session.flush()
                await self.session.refresh(model)
                
                tracking.updated_at = model.updated_at
                logger.info(f"Updated audience tracking {model.id}")

        return tracking

    async def get_by_id(self, tracking_id: TrackingId) -> Optional[AudienceTracking]:
        """Get tracking by ID."""
        stmt = select(AudienceTrackingModel).where(
            AudienceTrackingModel.id == tracking_id.value
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model:
            return self._to_aggregate(model)
        return None

    async def get_by_user_id(self, user_id: int) -> List[AudienceTracking]:
        """Get all trackings for a user."""
        stmt = select(AudienceTrackingModel).where(
            AudienceTrackingModel.user_id == user_id
        ).order_by(AudienceTrackingModel.created_at.desc())
        
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        return [self._to_aggregate(model) for model in models]

    async def get_active_by_user_id(self, user_id: int) -> List[AudienceTracking]:
        """Get active trackings for a user."""
        stmt = select(AudienceTrackingModel).where(
            and_(
                AudienceTrackingModel.user_id == user_id,
                AudienceTrackingModel.is_active == True,
                AudienceTrackingModel.expires_at > datetime.utcnow(),
            )
        ).order_by(AudienceTrackingModel.created_at.desc())
        
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        return [self._to_aggregate(model) for model in models]

    async def get_by_user_and_target(
        self, user_id: int, target_username: str
    ) -> Optional[AudienceTracking]:
        """Get tracking by user and target username."""
        stmt = select(AudienceTrackingModel).where(
            and_(
                AudienceTrackingModel.user_id == user_id,
                AudienceTrackingModel.target_username == target_username,
            )
        ).order_by(AudienceTrackingModel.created_at.desc())
        
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model:
            return self._to_aggregate(model)
        return None

    async def get_expired_subscriptions(self) -> List[AudienceTracking]:
        """Get all expired but still active subscriptions."""
        stmt = select(AudienceTrackingModel).where(
            and_(
                AudienceTrackingModel.is_active == True,
                AudienceTrackingModel.expires_at <= datetime.utcnow(),
            )
        )
        
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        return [self._to_aggregate(model) for model in models]

    async def get_subscriptions_for_renewal(self) -> List[AudienceTracking]:
        """Get subscriptions that need auto-renewal."""
        # Get subscriptions expiring in next 24 hours with auto_renew enabled
        tomorrow = datetime.utcnow() + timedelta(days=1)
        
        stmt = select(AudienceTrackingModel).where(
            and_(
                AudienceTrackingModel.is_active == True,
                AudienceTrackingModel.auto_renew == True,
                AudienceTrackingModel.expires_at <= tomorrow,
                AudienceTrackingModel.expires_at > datetime.utcnow(),
            )
        )
        
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        return [self._to_aggregate(model) for model in models]

    async def delete(self, tracking_id: TrackingId) -> bool:
        """Delete tracking subscription."""
        stmt = select(AudienceTrackingModel).where(
            AudienceTrackingModel.id == tracking_id.value
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model:
            await self.session.delete(model)
            await self.session.flush()
            logger.info(f"Deleted audience tracking {tracking_id.value}")
            return True
        
        return False

    def _to_model(self, tracking: AudienceTracking) -> AudienceTrackingModel:
        """Convert aggregate to model."""
        return AudienceTrackingModel(
            user_id=tracking.user_id,
            target_username=tracking.target_username,
            target_user_id=tracking.target_user_id,
            is_active=tracking.is_active,
            expires_at=tracking.expires_at,
            auto_renew=tracking.auto_renew,
            payment_id=tracking.payment_id,
            amount_paid=tracking.amount_paid,
            currency=tracking.currency,
            last_follower_count=tracking.last_follower_count.value if tracking.last_follower_count else None,
            last_following_count=tracking.last_following_count.value if tracking.last_following_count else None,
            last_checked_at=tracking.last_checked_at,
        )

    def _update_model(self, model: AudienceTrackingModel, tracking: AudienceTracking) -> None:
        """Update model from aggregate."""
        model.is_active = tracking.is_active
        model.expires_at = tracking.expires_at
        model.auto_renew = tracking.auto_renew
        model.payment_id = tracking.payment_id
        model.amount_paid = tracking.amount_paid
        model.currency = tracking.currency
        model.last_follower_count = tracking.last_follower_count.value if tracking.last_follower_count else None
        model.last_following_count = tracking.last_following_count.value if tracking.last_following_count else None
        model.last_checked_at = tracking.last_checked_at

    def _to_aggregate(self, model: AudienceTrackingModel) -> AudienceTracking:
        """Convert model to aggregate."""
        tracking = AudienceTracking(
            id=str(model.id),
            tracking_id=TrackingId(model.id),
            user_id=model.user_id,
            target_username=model.target_username,
            target_user_id=model.target_user_id,
            is_active=model.is_active,
            expires_at=model.expires_at,
            auto_renew=model.auto_renew,
            payment_id=model.payment_id,
            amount_paid=model.amount_paid,
            currency=model.currency,
            last_follower_count=FollowerCount(model.last_follower_count) if model.last_follower_count else None,
            last_following_count=FollowingCount(model.last_following_count) if model.last_following_count else None,
            last_checked_at=model.last_checked_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
        
        return tracking
