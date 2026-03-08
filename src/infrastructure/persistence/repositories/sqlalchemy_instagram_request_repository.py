"""SQLAlchemy implementation of Instagram Request repository."""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import async_sessionmaker

from ....domain.instagram_integration.entities.instagram_request import InstagramRequest
from ....domain.instagram_integration.repositories.instagram_request_repository import (
    InstagramRequestRepository
)
from ....domain.instagram_integration.value_objects.request_type import (
    RequestType,
    RequestTypeEnum
)
from ....domain.instagram_integration.value_objects.request_status import (
    RequestStatus,
    RequestStatusEnum
)
from ..models.instagram_request_model import InstagramRequestModel


class SqlAlchemyInstagramRequestRepository(InstagramRequestRepository):
    """SQLAlchemy implementation of Instagram Request repository."""
    
    def __init__(self, session_factory: async_sessionmaker):
        """Initialize repository."""
        self.session_factory = session_factory
    
    async def save(self, request: InstagramRequest) -> InstagramRequest:
        """Save Instagram request."""
        async with self.session_factory() as session:
            # Generate ID if not exists
            if request.id is None:
                request.id = str(uuid4())
            
            model = InstagramRequestModel(
                id=request.id,
                user_id=request.user_id,
                request_type=request.request_type.value.value,
                target_username=request.target_username,
                status=request.status.value.value,
                error_message=request.error_message,
                response_time_ms=request.response_time_ms,
                created_at=request.created_at,
            )
            
            session.add(model)
            await session.commit()
            await session.refresh(model)
            
            return self._to_entity(model)
    
    async def get_by_id(self, request_id: str) -> Optional[InstagramRequest]:
        """Get request by ID."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(InstagramRequestModel).where(
                    InstagramRequestModel.id == request_id
                )
            )
            model = result.scalar_one_or_none()
            
            if model is None:
                return None
            
            return self._to_entity(model)
    
    async def get_user_requests(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[InstagramRequest]:
        """Get user's request history."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(InstagramRequestModel)
                .where(InstagramRequestModel.user_id == user_id)
                .order_by(InstagramRequestModel.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            models = result.scalars().all()
            
            return [self._to_entity(model) for model in models]
    
    async def get_user_requests_by_type(
        self,
        user_id: str,
        request_type: RequestType,
        limit: int = 100
    ) -> List[InstagramRequest]:
        """Get user's requests by type."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(InstagramRequestModel)
                .where(
                    InstagramRequestModel.user_id == user_id,
                    InstagramRequestModel.request_type == request_type.value.value
                )
                .order_by(InstagramRequestModel.created_at.desc())
                .limit(limit)
            )
            models = result.scalars().all()
            
            return [self._to_entity(model) for model in models]
    
    async def get_user_requests_by_date_range(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[InstagramRequest]:
        """Get user's requests within date range."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(InstagramRequestModel)
                .where(
                    InstagramRequestModel.user_id == user_id,
                    InstagramRequestModel.created_at >= start_date,
                    InstagramRequestModel.created_at <= end_date
                )
                .order_by(InstagramRequestModel.created_at.desc())
            )
            models = result.scalars().all()
            
            return [self._to_entity(model) for model in models]
    
    async def count_user_requests_today(self, user_id: str) -> int:
        """Count user's requests today."""
        async with self.session_factory() as session:
            today_start = datetime.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            
            result = await session.execute(
                select(func.count(InstagramRequestModel.id))
                .where(
                    InstagramRequestModel.user_id == user_id,
                    InstagramRequestModel.created_at >= today_start
                )
            )
            count = result.scalar()
            
            return count or 0
    
    async def count_failed_requests(
        self,
        user_id: str,
        since: datetime
    ) -> int:
        """Count failed requests since given time."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(func.count(InstagramRequestModel.id))
                .where(
                    InstagramRequestModel.user_id == user_id,
                    InstagramRequestModel.created_at >= since,
                    InstagramRequestModel.status.in_([
                        RequestStatusEnum.FAILED.value,
                        RequestStatusEnum.RATE_LIMITED.value,
                        RequestStatusEnum.UNAUTHORIZED.value,
                        RequestStatusEnum.NOT_FOUND.value,
                    ])
                )
            )
            count = result.scalar()
            
            return count or 0
    
    async def get_recent_requests(
        self,
        limit: int = 100
    ) -> List[InstagramRequest]:
        """Get recent requests (for admin/analytics)."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(InstagramRequestModel)
                .order_by(InstagramRequestModel.created_at.desc())
                .limit(limit)
            )
            models = result.scalars().all()
            
            return [self._to_entity(model) for model in models]
    
    def _to_entity(self, model: InstagramRequestModel) -> InstagramRequest:
        """Convert model to entity."""
        return InstagramRequest(
            id=model.id,
            user_id=model.user_id,
            request_type=RequestType(value=RequestTypeEnum(model.request_type)),
            target_username=model.target_username,
            status=RequestStatus(value=RequestStatusEnum(model.status)),
            error_message=model.error_message,
            response_time_ms=model.response_time_ms,
            created_at=model.created_at,
        )
