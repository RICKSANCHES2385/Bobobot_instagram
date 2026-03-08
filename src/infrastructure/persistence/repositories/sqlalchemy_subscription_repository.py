"""SQLAlchemy implementation of Subscription repository."""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.domain.subscription.aggregates.subscription import Subscription
from src.domain.subscription.repositories.subscription_repository import SubscriptionRepository
from src.domain.subscription.value_objects.subscription_id import SubscriptionId
from src.domain.user_management.value_objects.user_id import UserId
from src.infrastructure.persistence.models.subscription_model import (
    SubscriptionModel,
    SubscriptionStatusEnum,
    SubscriptionTypeEnum,
)
from src.domain.subscription.value_objects.subscription_status import SubscriptionStatus
from src.domain.subscription.value_objects.subscription_type import SubscriptionType
from src.domain.subscription.value_objects.subscription_period import SubscriptionPeriod
from src.domain.shared.value_objects.money import Money


class SQLAlchemySubscriptionRepository(SubscriptionRepository):
    """SQLAlchemy implementation of subscription repository."""
    
    def __init__(self, session: Session):
        self._session = session
    
    async def save(self, subscription: Subscription) -> None:
        """Save subscription to database."""
        try:
            model = self._session.query(SubscriptionModel).filter_by(
                id=str(subscription.id.value)
            ).first()
            
            if model:
                self._update_model(model, subscription)
            else:
                model = self._to_model(subscription)
                self._session.add(model)
            
            self._session.flush()
        except SQLAlchemyError as e:
            self._session.rollback()
            raise RuntimeError(f"Failed to save subscription: {str(e)}") from e
    
    async def get_by_id(self, subscription_id: SubscriptionId) -> Optional[Subscription]:
        """Find subscription by ID."""
        try:
            model = self._session.query(SubscriptionModel).filter_by(
                id=str(subscription_id.value)
            ).first()
            
            return self._to_domain(model) if model else None
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to find subscription: {str(e)}") from e
    
    async def get_active_by_user_id(self, user_id: UserId) -> Optional[Subscription]:
        """Find active subscription for user."""
        try:
            model = self._session.query(SubscriptionModel).filter_by(
                user_id=str(user_id.value),
                status=SubscriptionStatusEnum.ACTIVE
            ).first()
            
            return self._to_domain(model) if model else None
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to find active subscription: {str(e)}") from e
    
    async def get_all_by_user_id(self, user_id: UserId) -> list[Subscription]:
        """Get all subscriptions for user."""
        try:
            models = self._session.query(SubscriptionModel).filter_by(
                user_id=str(user_id.value)
            ).all()
            
            return [self._to_domain(model) for model in models]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to find subscriptions: {str(e)}") from e
    
    async def delete(self, subscription_id: SubscriptionId) -> None:
        """Delete subscription from database."""
        try:
            self._session.query(SubscriptionModel).filter_by(
                id=str(subscription_id.value)
            ).delete()
            self._session.flush()
        except SQLAlchemyError as e:
            self._session.rollback()
            raise RuntimeError(f"Failed to delete subscription: {str(e)}") from e
    
    def _to_model(self, subscription: Subscription) -> SubscriptionModel:
        """Convert domain subscription to database model."""
        return SubscriptionModel(
            id=str(subscription.id.value),
            user_id=str(subscription.user_id.value),
            type=self._map_type_to_enum(subscription.type),
            status=self._map_status_to_enum(subscription.status),
            start_date=subscription.period.start_date,
            end_date=subscription.period.end_date,
            price_amount=float(subscription.price.amount),
            price_currency=subscription.price.currency,
            auto_renew=1 if subscription.auto_renew else 0,
        )
    
    def _update_model(self, model: SubscriptionModel, subscription: Subscription) -> None:
        """Update existing model with subscription data."""
        model.user_id = str(subscription.user_id.value)
        model.type = self._map_type_to_enum(subscription.type)
        model.status = self._map_status_to_enum(subscription.status)
        model.start_date = subscription.period.start_date
        model.end_date = subscription.period.end_date
        model.price_amount = float(subscription.price.amount)
        model.price_currency = subscription.price.currency
        model.auto_renew = 1 if subscription.auto_renew else 0
    
    def _to_domain(self, model: SubscriptionModel) -> Subscription:
        """Convert database model to domain subscription."""
        from uuid import UUID
        subscription = Subscription(
            id=SubscriptionId(UUID(model.id)),
            user_id=UserId(int(model.user_id)),
            type=self._map_enum_to_type(model.type),
            status=self._map_enum_to_status(model.status),
            period=SubscriptionPeriod(model.start_date, model.end_date),
            price=Money(float(model.price_amount), model.price_currency),
            auto_renew=bool(model.auto_renew),
        )
        return subscription
    
    @staticmethod
    def _map_type_to_enum(sub_type: SubscriptionType) -> SubscriptionTypeEnum:
        """Map domain subscription type to database enum."""
        from src.domain.subscription.value_objects.subscription_type import SubscriptionTypeEnum as DomainEnum
        
        mapping = {
            DomainEnum.FREE: SubscriptionTypeEnum.FREE,
            DomainEnum.BASIC: SubscriptionTypeEnum.BASIC,
            DomainEnum.PREMIUM: SubscriptionTypeEnum.PREMIUM,
        }
        return mapping[sub_type.type]
    
    @staticmethod
    def _map_enum_to_type(enum_value: SubscriptionTypeEnum) -> SubscriptionType:
        """Map database enum to domain subscription type."""
        from src.domain.subscription.value_objects.subscription_type import SubscriptionTypeEnum as DomainEnum
        
        mapping = {
            SubscriptionTypeEnum.FREE: SubscriptionType(type=DomainEnum.FREE),
            SubscriptionTypeEnum.BASIC: SubscriptionType(type=DomainEnum.BASIC),
            SubscriptionTypeEnum.PREMIUM: SubscriptionType(type=DomainEnum.PREMIUM),
        }
        return mapping[enum_value]
    
    @staticmethod
    def _map_status_to_enum(status: SubscriptionStatus) -> SubscriptionStatusEnum:
        """Map domain subscription status to database enum."""
        from src.domain.subscription.value_objects.subscription_status import SubscriptionStatusEnum as DomainEnum
        
        mapping = {
            DomainEnum.ACTIVE: SubscriptionStatusEnum.ACTIVE,
            DomainEnum.EXPIRED: SubscriptionStatusEnum.EXPIRED,
            DomainEnum.CANCELLED: SubscriptionStatusEnum.CANCELLED,
        }
        return mapping[status.status]

    @staticmethod
    def _map_enum_to_status(enum_value: SubscriptionStatusEnum) -> SubscriptionStatus:
        """Map database enum to domain subscription status."""
        from src.domain.subscription.value_objects.subscription_status import SubscriptionStatusEnum as DomainEnum
        
        mapping = {
            SubscriptionStatusEnum.ACTIVE: SubscriptionStatus(status=DomainEnum.ACTIVE),
            SubscriptionStatusEnum.EXPIRED: SubscriptionStatus(status=DomainEnum.EXPIRED),
            SubscriptionStatusEnum.CANCELLED: SubscriptionStatus(status=DomainEnum.CANCELLED),
        }
        return mapping[enum_value]
