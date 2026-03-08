"""Tests for Money."""
import pytest
from decimal import Decimal
from src.domain.shared.value_objects.money import Money, Currency


def test_money_creation():
    """Money should be created with amount and currency."""
    money = Money(amount=Decimal("100.50"), currency=Currency.RUB)
    
    assert money.amount == Decimal("100.50")
    assert money.currency == Currency.RUB
    assert str(money) == "100.50 RUB"


def test_money_validates_negative():
    """Money should not accept negative amounts."""
    with pytest.raises(ValueError, match="Amount cannot be negative"):
        Money(amount=Decimal("-10"), currency=Currency.RUB)


def test_money_add_same_currency():
    """Money should add amounts with same currency."""
    money1 = Money(amount=Decimal("100"), currency=Currency.RUB)
    money2 = Money(amount=Decimal("50"), currency=Currency.RUB)
    
    result = money1.add(money2)
    
    assert result.amount == Decimal("150")
    assert result.currency == Currency.RUB


def test_money_add_different_currency_raises():
    """Money should not add amounts with different currencies."""
    money1 = Money(amount=Decimal("100"), currency=Currency.RUB)
    money2 = Money(amount=Decimal("50"), currency=Currency.XTR)
    
    with pytest.raises(ValueError, match="Cannot add money with different currencies"):
        money1.add(money2)


def test_money_subtract():
    """Money should subtract amounts."""
    money1 = Money(amount=Decimal("100"), currency=Currency.RUB)
    money2 = Money(amount=Decimal("30"), currency=Currency.RUB)
    
    result = money1.subtract(money2)
    
    assert result.amount == Decimal("70")
    assert result.currency == Currency.RUB


def test_money_subtract_negative_result_raises():
    """Money subtraction should not result in negative amount."""
    money1 = Money(amount=Decimal("50"), currency=Currency.RUB)
    money2 = Money(amount=Decimal("100"), currency=Currency.RUB)
    
    with pytest.raises(ValueError, match="Result cannot be negative"):
        money1.subtract(money2)


def test_money_multiply():
    """Money should multiply by a factor."""
    money = Money(amount=Decimal("100"), currency=Currency.RUB)
    
    result = money.multiply(2)
    
    assert result.amount == Decimal("200")
    assert result.currency == Currency.RUB


def test_money_multiply_decimal():
    """Money should multiply by decimal factor."""
    money = Money(amount=Decimal("100"), currency=Currency.RUB)
    
    result = money.multiply(Decimal("1.5"))
    
    assert result.amount == Decimal("150")
    assert result.currency == Currency.RUB
