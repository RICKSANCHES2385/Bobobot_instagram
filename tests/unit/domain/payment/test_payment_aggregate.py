"""Tests for Payment Aggregate."""
import pytest
from datetime import datetime

from src.domain.payment.aggregates.payment import Payment
from src.domain.payment.value_objects.payment_id import PaymentId
from src.domain.payment.value_objects.payment_status import PaymentStatus
from src.domain.payment.value_objects.payment_method import PaymentMethod
from src.domain.payment.events.payment_events import (
    PaymentCreated,
    PaymentProcessing,
    PaymentCompleted,
    PaymentFailed,
    PaymentCancelled,
    PaymentRefunded
)
from src.domain.payment.exceptions import (
    InvalidPaymentStateException,
    InvalidPaymentAmountException
)
from src.domain.shared.value_objects.money import Money
from src.domain.user_management.value_objects.user_id import UserId


class TestPaymentCreation:
    """Tests for payment creation."""
    
    def test_payment_create_success(self):
        """Test successful payment creation."""
        # Arrange
        user_id = UserId(value=123)
        amount = Money(amount=100.0, currency="RUB")
        method = PaymentMethod.telegram_stars()
        
        # Act
        payment = Payment.create(
            user_id=user_id,
            amount=amount,
            method=method
        )
        
        # Assert
        assert payment.user_id == user_id
        assert payment.amount == amount
        assert payment.method == method
        assert payment.status.is_pending()
        assert payment.transaction_id is None
        assert payment.failure_reason is None
        assert payment.refund_amount is None
        assert isinstance(payment.created_at, datetime)
        assert isinstance(payment.updated_at, datetime)
    
    def test_payment_create_generates_event(self):
        """Test that payment creation generates PaymentCreated event."""
        # Arrange
        user_id = UserId(value=123)
        amount = Money(amount=100.0, currency="RUB")
        method = PaymentMethod.telegram_stars()
        
        # Act
        payment = Payment.create(
            user_id=user_id,
            amount=amount,
            method=method
        )
        
        # Assert
        events = payment.domain_events
        assert len(events) == 1
        assert isinstance(events[0], PaymentCreated)
        assert events[0].payment_id == payment.id.value
        assert events[0].user_id == user_id.value
        assert events[0].amount == amount.amount
        assert events[0].currency == amount.currency
        assert events[0].method == method.value.value
    
    def test_payment_create_with_zero_amount_raises_exception(self):
        """Test that creating payment with zero amount raises exception."""
        # Arrange
        user_id = UserId(value=123)
        amount = Money(amount=0.0, currency="RUB")
        method = PaymentMethod.telegram_stars()
        
        # Act & Assert
        with pytest.raises(InvalidPaymentAmountException):
            Payment.create(
                user_id=user_id,
                amount=amount,
                method=method
            )
    
    def test_payment_create_with_negative_amount_raises_exception(self):
        """Test that creating payment with negative amount raises exception."""
        # Arrange
        user_id = UserId(value=123)
        method = PaymentMethod.telegram_stars()
        
        # Act & Assert
        # Money itself validates negative amounts
        with pytest.raises(ValueError, match="Amount cannot be negative"):
            amount = Money(amount=-100.0, currency="RUB")
            Payment.create(
                user_id=user_id,
                amount=amount,
                method=method
            )


class TestPaymentProcessing:
    """Tests for payment processing."""
    
    def test_payment_process_success(self):
        """Test successful payment processing."""
        # Arrange
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        payment.clear_domain_events()
        
        # Act
        payment.process()
        
        # Assert
        assert payment.status.is_processing()
    
    def test_payment_process_generates_event(self):
        """Test that payment processing generates PaymentProcessing event."""
        # Arrange
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        payment.clear_domain_events()
        
        # Act
        payment.process()
        
        # Assert
        events = payment.domain_events
        assert len(events) == 1
        assert isinstance(events[0], PaymentProcessing)
        assert events[0].payment_id == payment.id.value
    
    def test_payment_process_from_processing_raises_exception(self):
        """Test that processing already processing payment raises exception."""
        # Arrange
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        payment.process()
        
        # Act & Assert
        with pytest.raises(InvalidPaymentStateException):
            payment.process()
    
    def test_payment_process_from_completed_raises_exception(self):
        """Test that processing completed payment raises exception."""
        # Arrange
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        payment.process()
        payment.complete()
        
        # Act & Assert
        with pytest.raises(InvalidPaymentStateException):
            payment.process()


class TestPaymentCompletion:
    """Tests for payment completion."""
    
    def test_payment_complete_success(self):
        """Test successful payment completion."""
        # Arrange
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        payment.process()
        payment.clear_domain_events()
        
        # Act
        payment.complete(transaction_id="txn_123")
        
        # Assert
        assert payment.status.is_completed()
        assert payment.transaction_id == "txn_123"
    
    def test_payment_complete_generates_event(self):
        """Test that payment completion generates PaymentCompleted event."""
        # Arrange
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        payment.process()
        payment.clear_domain_events()
        
        # Act
        payment.complete(transaction_id="txn_123")
        
        # Assert
        events = payment.domain_events
        assert len(events) == 1
        assert isinstance(events[0], PaymentCompleted)
        assert events[0].payment_id == payment.id.value
        assert events[0].transaction_id == "txn_123"
    
    def test_payment_complete_from_pending_raises_exception(self):
        """Test that completing pending payment raises exception."""
        # Arrange
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        
        # Act & Assert
        with pytest.raises(InvalidPaymentStateException):
            payment.complete()
    
    def test_payment_complete_from_completed_raises_exception(self):
        """Test that completing already completed payment raises exception."""
        # Arrange
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        payment.process()
        payment.complete()
        
        # Act & Assert
        with pytest.raises(InvalidPaymentStateException):
            payment.complete()


class TestPaymentFailure:
    """Tests for payment failure."""
    
    def test_payment_fail_from_pending_success(self):
        """Test successful payment failure from pending."""
        # Arrange
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        payment.clear_domain_events()
        
        # Act
        payment.fail(reason="Insufficient funds")
        
        # Assert
        assert payment.status.is_failed()
        assert payment.failure_reason == "Insufficient funds"
    
    def test_payment_fail_from_processing_success(self):
        """Test successful payment failure from processing."""
        # Arrange
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        payment.process()
        payment.clear_domain_events()
        
        # Act
        payment.fail(reason="Payment gateway error")
        
        # Assert
        assert payment.status.is_failed()
        assert payment.failure_reason == "Payment gateway error"
    
    def test_payment_fail_generates_event(self):
        """Test that payment failure generates PaymentFailed event."""
        # Arrange
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        payment.clear_domain_events()
        
        # Act
        payment.fail(reason="Test failure")
        
        # Assert
        events = payment.domain_events
        assert len(events) == 1
        assert isinstance(events[0], PaymentFailed)
        assert events[0].payment_id == payment.id.value
        assert events[0].reason == "Test failure"
    
    def test_payment_fail_from_completed_raises_exception(self):
        """Test that failing completed payment raises exception."""
        # Arrange
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        payment.process()
        payment.complete()
        
        # Act & Assert
        with pytest.raises(InvalidPaymentStateException):
            payment.fail(reason="Test")


class TestPaymentCancellation:
    """Tests for payment cancellation."""
    
    def test_payment_cancel_success(self):
        """Test successful payment cancellation."""
        # Arrange
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        payment.clear_domain_events()
        
        # Act
        payment.cancel(reason="User cancelled")
        
        # Assert
        assert payment.status.is_cancelled()
        assert payment.failure_reason == "User cancelled"
    
    def test_payment_cancel_generates_event(self):
        """Test that payment cancellation generates PaymentCancelled event."""
        # Arrange
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        payment.clear_domain_events()
        
        # Act
        payment.cancel(reason="User cancelled")
        
        # Assert
        events = payment.domain_events
        assert len(events) == 1
        assert isinstance(events[0], PaymentCancelled)
        assert events[0].payment_id == payment.id.value
        assert events[0].reason == "User cancelled"
    
    def test_payment_cancel_from_processing_raises_exception(self):
        """Test that cancelling processing payment raises exception."""
        # Arrange
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        payment.process()
        
        # Act & Assert
        with pytest.raises(InvalidPaymentStateException):
            payment.cancel()


class TestPaymentRefund:
    """Tests for payment refund."""
    
    def test_payment_refund_success(self):
        """Test successful payment refund."""
        # Arrange
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        payment.process()
        payment.complete()
        payment.clear_domain_events()
        
        refund_amount = Money(amount=100.0, currency="RUB")
        
        # Act
        payment.refund(refund_amount=refund_amount, reason="Customer request")
        
        # Assert
        assert payment.status.is_refunded()
        assert payment.refund_amount == refund_amount
        assert payment.failure_reason == "Customer request"
    
    def test_payment_refund_partial_success(self):
        """Test successful partial payment refund."""
        # Arrange
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        payment.process()
        payment.complete()
        payment.clear_domain_events()
        
        refund_amount = Money(amount=50.0, currency="RUB")
        
        # Act
        payment.refund(refund_amount=refund_amount)
        
        # Assert
        assert payment.status.is_refunded()
        assert payment.refund_amount.amount == 50.0
    
    def test_payment_refund_generates_event(self):
        """Test that payment refund generates PaymentRefunded event."""
        # Arrange
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        payment.process()
        payment.complete()
        payment.clear_domain_events()
        
        refund_amount = Money(amount=100.0, currency="RUB")
        
        # Act
        payment.refund(refund_amount=refund_amount, reason="Test refund")
        
        # Assert
        events = payment.domain_events
        assert len(events) == 1
        assert isinstance(events[0], PaymentRefunded)
        assert events[0].payment_id == payment.id.value
        assert events[0].refund_amount == 100.0
        assert events[0].reason == "Test refund"
    
    def test_payment_refund_from_pending_raises_exception(self):
        """Test that refunding pending payment raises exception."""
        # Arrange
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        refund_amount = Money(amount=100.0, currency="RUB")
        
        # Act & Assert
        with pytest.raises(InvalidPaymentStateException):
            payment.refund(refund_amount=refund_amount)
    
    def test_payment_refund_with_zero_amount_raises_exception(self):
        """Test that refunding with zero amount raises exception."""
        # Arrange
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        payment.process()
        payment.complete()
        
        refund_amount = Money(amount=0.0, currency="RUB")
        
        # Act & Assert
        with pytest.raises(InvalidPaymentAmountException):
            payment.refund(refund_amount=refund_amount)
    
    def test_payment_refund_with_excessive_amount_raises_exception(self):
        """Test that refunding more than payment amount raises exception."""
        # Arrange
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        payment.process()
        payment.complete()
        
        refund_amount = Money(amount=150.0, currency="RUB")
        
        # Act & Assert
        with pytest.raises(InvalidPaymentAmountException):
            payment.refund(refund_amount=refund_amount)
    
    def test_payment_refund_with_different_currency_raises_exception(self):
        """Test that refunding with different currency raises exception."""
        # Arrange
        payment = Payment.create(
            user_id=UserId(value=123),
            amount=Money(amount=100.0, currency="RUB"),
            method=PaymentMethod.telegram_stars()
        )
        payment.process()
        payment.complete()
        
        refund_amount = Money(amount=100.0, currency="USD")
        
        # Act & Assert
        with pytest.raises(InvalidPaymentAmountException):
            payment.refund(refund_amount=refund_amount)
