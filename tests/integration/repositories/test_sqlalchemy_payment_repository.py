"""Integration tests for SQLAlchemy Payment Repository."""
import pytest
from uuid import uuid4

from src.domain.payment.aggregates.payment import Payment
from src.domain.payment.value_objects.payment_id import PaymentId
from src.domain.payment.value_objects.payment_method import PaymentMethod
from src.domain.shared.value_objects.money import Money
from src.domain.user_management.value_objects.user_id import UserId
from src.infrastructure.persistence.repositories.sqlalchemy_payment_repository import SQLAlchemyPaymentRepository


@pytest.mark.integration
@pytest.mark.asyncio
class TestSQLAlchemyPaymentRepository:
    """Tests for SQLAlchemy Payment Repository."""
    
    @pytest.fixture
    def repository(self, async_session):
        """Create repository instance."""
        return SQLAlchemyPaymentRepository(async_session)
    
    async def test_save_new_payment(self, repository, async_session):
        """Test saving a new payment."""
        # Arrange
        
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        
        # Act
        await repository.save(payment)
        await async_session.commit()
        
        # Assert
        retrieved = await repository.get_by_id(payment.id)
        assert retrieved is not None
        assert retrieved.id == payment.id
        assert retrieved.user_id.value == 123
        assert retrieved.amount.amount == 100.0
        assert retrieved.status.is_pending()
    
    async def test_save_updates_existing_payment(self, repository, async_session):
        """Test that save updates existing payment."""
        # Arrange
        
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        await repository.save(payment)
        await async_session.commit()
        
        # Act - update payment
        payment.process()
        await repository.save(payment)
        await async_session.commit()
        
        # Assert
        retrieved = await repository.get_by_id(payment.id)
        assert retrieved.status.is_processing()
    
    async def test_get_by_id_existing_payment(self, repository, async_session):
        """Test getting existing payment by ID."""
        # Arrange
        
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        await repository.save(payment)
        await async_session.commit()
        
        # Act
        retrieved = await repository.get_by_id(payment.id)
        
        # Assert
        assert retrieved is not None
        assert retrieved.id == payment.id
    
    async def test_get_by_id_not_found(self, repository, async_session):
        """Test getting non-existent payment returns None."""
        # Arrange
        
        payment_id = PaymentId(value=uuid4())
        
        # Act
        retrieved = await repository.get_by_id(payment_id)
        
        # Assert
        assert retrieved is None
    
    async def test_get_by_user_id(self, repository, async_session):
        """Test getting all payments for a user."""
        # Arrange
        
        user_id = UserId(value=123)
        
        payment1 = Payment.create(
            user_id=user_id,
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        payment2 = Payment.create(
            user_id=user_id,
            amount=Money(amount=200.0, currency="RUB"),
            method=PaymentMethod.robokassa()
        )
        
        await repository.save(payment1)
        await repository.save(payment2)
        await async_session.commit()
        
        # Act
        payments = await repository.get_by_user_id(user_id)
        
        # Assert
        assert len(payments) == 2
        assert all(p.user_id == user_id for p in payments)
    
    async def test_get_by_user_id_no_payments(self, repository, async_session):
        """Test getting payments for user with no payments."""
        # Arrange
        
        user_id = UserId(value=999)
        
        # Act
        payments = await repository.get_by_user_id(user_id)
        
        # Assert
        assert len(payments) == 0
    
    async def test_get_by_transaction_id(self, repository, async_session):
        """Test getting payment by transaction ID."""
        # Arrange
        
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        payment.process()
        payment.complete(transaction_id="txn_123")
        
        await repository.save(payment)
        await async_session.commit()
        
        # Act
        retrieved = await repository.get_by_transaction_id("txn_123")
        
        # Assert
        assert retrieved is not None
        assert retrieved.transaction_id == "txn_123"
    
    async def test_get_by_transaction_id_not_found(self, repository, async_session):
        """Test getting payment by non-existent transaction ID."""
        # Arrange
        
        
        # Act
        retrieved = await repository.get_by_transaction_id("non_existent")
        
        # Assert
        assert retrieved is None
    
    async def test_payment_status_persistence(self, repository, async_session):
        """Test that payment status changes are persisted."""
        # Arrange
        
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        await repository.save(payment)
        await async_session.commit()
        
        # Act - process and complete
        payment.process()
        await repository.save(payment)
        await async_session.commit()
        
        payment.complete(transaction_id="txn_123")
        await repository.save(payment)
        await async_session.commit()
        
        # Assert
        retrieved = await repository.get_by_id(payment.id)
        assert retrieved.status.is_completed()
        assert retrieved.transaction_id == "txn_123"
    
    async def test_payment_refund_persistence(self, repository, async_session):
        """Test that payment refund is persisted."""
        # Arrange
        
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        payment.process()
        payment.complete()
        await repository.save(payment)
        await async_session.commit()
        
        # Act - refund
        refund_amount = Money(amount=50.0, currency="RUB")
        payment.refund(refund_amount=refund_amount, reason="Customer request")
        await repository.save(payment)
        await async_session.commit()
        
        # Assert
        retrieved = await repository.get_by_id(payment.id)
        assert retrieved.status.is_refunded()
        assert retrieved.refund_amount.amount == 50.0
        assert retrieved.failure_reason == "Customer request"
    
    async def test_payment_method_persistence(self, repository, async_session):
        """Test that different payment methods are persisted correctly."""
        # Arrange
        
        
        payment1 = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        payment2 = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=200.0, currency="RUB"),
            method=PaymentMethod.robokassa()
        )
        payment3 = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=10.0, currency="TON"),
            method=PaymentMethod.crypto_bot()
        )
        
        await repository.save(payment1)
        await repository.save(payment2)
        await repository.save(payment3)
        await async_session.commit()
        
        # Act & Assert
        retrieved1 = await repository.get_by_id(payment1.id)
        assert retrieved1.method.is_telegram_stars()
        
        retrieved2 = await repository.get_by_id(payment2.id)
        assert retrieved2.method.is_robokassa()
        
        retrieved3 = await repository.get_by_id(payment3.id)
        assert retrieved3.method.is_crypto_bot()
