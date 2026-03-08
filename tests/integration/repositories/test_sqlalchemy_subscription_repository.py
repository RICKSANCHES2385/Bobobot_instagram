"""Integration tests for SQLAlchemy Subscription Repository."""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.infrastructure.persistence.base import Base
from src.infrastructure.persistence.models.user_model import UserModel
from src.infrastructure.persistence.models.subscription_model import (
    SubscriptionModel,
    SubscriptionStatusEnum,
    SubscriptionTypeEnum,
)
from src.infrastructure.persistence.repositories.sqlalchemy_subscription_repository import (
    SQLAlchemySubscriptionRepository,
)
from src.domain.subscription.aggregates.subscription import Subscription
from src.domain.subscription.value_objects.subscription_id import SubscriptionId
from src.domain.subscription.value_objects.subscription_type import SubscriptionType
from src.domain.subscription.value_objects.subscription_period import SubscriptionPeriod
from src.domain.user_management.value_objects.user_id import UserId
from src.domain.shared.value_objects.money import Money


@pytest.fixture
def engine():
    """Create in-memory SQLite engine."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine) -> Session:
    """Create database session."""
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def repository(session):
    """Create repository instance."""
    return SQLAlchemySubscriptionRepository(session)


@pytest.fixture
def test_user(session) -> UserModel:
    """Create test user in database."""
    user = UserModel(
        id="123456789",
        telegram_username="testuser",
        first_name="Test",
        last_name="User",
        is_active=True,
    )
    session.add(user)
    session.commit()
    return user


class TestSQLAlchemySubscriptionRepository:
    """Test suite for SQLAlchemy subscription repository."""
    
    @pytest.mark.asyncio
    async def test_save_new_subscription(self, repository, session, test_user):
        """Test saving new subscription."""
        # Arrange
        subscription = Subscription.create(
            user_id=UserId(int(test_user.id)),
            subscription_type=SubscriptionType.basic(),
            period=SubscriptionPeriod(
                datetime.utcnow(),
                datetime.utcnow() + timedelta(days=30)
            ),
            price=Money(Decimal("9.99"), "USD"),
        )
        
        # Act
        await repository.save(subscription)
        session.commit()
        
        # Assert
        model = session.query(SubscriptionModel).filter_by(
            id=str(subscription.id.value)
        ).first()
        
        assert model is not None
        assert model.user_id == test_user.id  # Integer comparison
        assert model.type == SubscriptionTypeEnum.BASIC
        assert model.status == SubscriptionStatusEnum.ACTIVE
        assert float(model.price_amount) == 9.99
        assert model.price_currency == "USD"
    
    @pytest.mark.asyncio
    async def test_save_updates_existing_subscription(self, repository, session, test_user):
        """Test updating existing subscription."""
        # Arrange
        subscription = Subscription.create(
            user_id=UserId(int(test_user.id)),
            subscription_type=SubscriptionType.basic(),
            period=SubscriptionPeriod(
                datetime.utcnow(),
                datetime.utcnow() + timedelta(days=30)
            ),
            price=Money(Decimal("9.99"), "USD"),
        )
        await repository.save(subscription)
        session.commit()
        
        # Act
        subscription.cancel()
        await repository.save(subscription)
        session.commit()
        
        # Assert
        model = session.query(SubscriptionModel).filter_by(
            id=str(subscription.id.value)
        ).first()
        
        assert model.status == SubscriptionStatusEnum.CANCELLED
    
    @pytest.mark.asyncio
    async def test_get_by_id_existing(self, repository, session, test_user):
        """Test finding subscription by ID."""
        # Arrange
        subscription = Subscription.create(
            user_id=UserId(int(test_user.id)),
            subscription_type=SubscriptionType.premium(),
            period=SubscriptionPeriod(
                datetime.utcnow(),
                datetime.utcnow() + timedelta(days=30)
            ),
            price=Money(Decimal("19.99"), "USD"),
        )
        await repository.save(subscription)
        session.commit()
        
        # Act
        found = await repository.get_by_id(subscription.id)
        
        # Assert
        assert found is not None
        assert found.id == subscription.id
        assert found.user_id == subscription.user_id
        assert found.type == SubscriptionType.premium()
        assert float(found.price.amount) == 19.99  # Compare as float
    
    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository):
        """Test finding non-existent subscription."""
        # Act
        found = await repository.get_by_id(SubscriptionId(uuid4()))
        
        # Assert
        assert found is None
    
    @pytest.mark.asyncio
    async def test_get_active_by_user_id(self, repository, session, test_user):
        """Test finding active subscription for user."""
        # Arrange
        subscription = Subscription.create(
            user_id=UserId(int(test_user.id)),
            subscription_type=SubscriptionType.basic(),
            period=SubscriptionPeriod(
                datetime.utcnow(),
                datetime.utcnow() + timedelta(days=30)
            ),
            price=Money(Decimal("9.99"), "USD"),
        )
        await repository.save(subscription)
        session.commit()
        
        # Act
        found = await repository.get_active_by_user_id(UserId(int(test_user.id)))
        
        # Assert
        assert found is not None
        assert found.id == subscription.id
        assert found.is_active()
    
    @pytest.mark.asyncio
    async def test_get_active_by_user_id_no_active(self, repository, session, test_user):
        """Test finding active subscription when none exists."""
        # Arrange
        subscription = Subscription.create(
            user_id=UserId(int(test_user.id)),
            subscription_type=SubscriptionType.basic(),
            period=SubscriptionPeriod(
                datetime.utcnow(),
                datetime.utcnow() + timedelta(days=30)
            ),
            price=Money(Decimal("9.99"), "USD"),
        )
        subscription.cancel()
        await repository.save(subscription)
        session.commit()
        
        # Act
        found = await repository.get_active_by_user_id(UserId(int(test_user.id)))
        
        # Assert
        assert found is None
    
    @pytest.mark.asyncio
    async def test_delete_subscription(self, repository, session, test_user):
        """Test deleting subscription."""
        # Arrange
        subscription = Subscription.create(
            user_id=UserId(int(test_user.id)),
            subscription_type=SubscriptionType.basic(),
            period=SubscriptionPeriod(
                datetime.utcnow(),
                datetime.utcnow() + timedelta(days=30)
            ),
            price=Money(Decimal("9.99"), "USD"),
        )
        await repository.save(subscription)
        session.commit()
        
        # Act
        await repository.delete(subscription.id)
        session.commit()
        
        # Assert
        model = session.query(SubscriptionModel).filter_by(
            id=str(subscription.id.value)
        ).first()
        assert model is None
    
    @pytest.mark.asyncio
    async def test_auto_renew_persistence(self, repository, session, test_user):
        """Test auto_renew flag persistence."""
        # Arrange
        subscription = Subscription.create(
            user_id=UserId(int(test_user.id)),
            subscription_type=SubscriptionType.basic(),
            period=SubscriptionPeriod(
                datetime.utcnow(),
                datetime.utcnow() + timedelta(days=30)
            ),
            price=Money(Decimal("9.99"), "USD"),
            auto_renew=True,
        )
        
        # Act
        await repository.save(subscription)
        session.commit()
        
        # Assert
        found = await repository.get_by_id(subscription.id)
        assert found.auto_renew is True
    
    @pytest.mark.asyncio
    async def test_subscription_period_persistence(self, repository, session, test_user):
        """Test subscription period dates persistence."""
        # Arrange
        start = datetime(2026, 1, 1, 12, 0, 0)
        end = datetime(2026, 2, 1, 12, 0, 0)
        
        subscription = Subscription.create(
            user_id=UserId(int(test_user.id)),
            subscription_type=SubscriptionType.basic(),
            period=SubscriptionPeriod(start, end),
            price=Money(Decimal("9.99"), "USD"),
        )
        
        # Act
        await repository.save(subscription)
        session.commit()
        
        # Assert
        found = await repository.get_by_id(subscription.id)
        assert found.period.start_date == start
        assert found.period.end_date == end
    
    @pytest.mark.asyncio
    async def test_get_all_by_user_id(self, repository, session, test_user):
        """Test getting all subscriptions for user."""
        # Arrange
        sub1 = Subscription.create(
            user_id=UserId(int(test_user.id)),
            subscription_type=SubscriptionType.basic(),
            period=SubscriptionPeriod(
                datetime.utcnow() - timedelta(days=60),
                datetime.utcnow() - timedelta(days=30)
            ),
            price=Money(Decimal("9.99"), "USD"),
        )
        sub1.cancel()
        
        sub2 = Subscription.create(
            user_id=UserId(int(test_user.id)),
            subscription_type=SubscriptionType.premium(),
            period=SubscriptionPeriod(
                datetime.utcnow(),
                datetime.utcnow() + timedelta(days=30)
            ),
            price=Money(Decimal("19.99"), "USD"),
        )
        
        # Act
        await repository.save(sub1)
        await repository.save(sub2)
        session.commit()
        
        # Assert
        all_subs = await repository.get_all_by_user_id(UserId(int(test_user.id)))
        assert len(all_subs) == 2
        
        active = await repository.get_active_by_user_id(UserId(int(test_user.id)))
        assert active is not None
        assert active.id == sub2.id
        assert active.type == SubscriptionType.premium()

