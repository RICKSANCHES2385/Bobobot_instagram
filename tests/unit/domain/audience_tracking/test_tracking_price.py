"""Tests for TrackingPrice value object."""

import pytest
from decimal import Decimal

from src.domain.audience_tracking.value_objects.tracking_price import TrackingPrice


class TestTrackingPrice:
    """Test TrackingPrice value object."""

    def test_create_valid_price(self):
        """Test creating valid price."""
        price = TrackingPrice(amount=Decimal("129.00"), currency="RUB")
        
        assert price.amount == Decimal("129.00")
        assert price.currency == "RUB"

    def test_create_price_with_int(self):
        """Test creating price with integer amount."""
        price = TrackingPrice(amount=576, currency="XTR")
        
        assert price.amount == Decimal("576")
        assert price.currency == "XTR"

    def test_create_price_with_float(self):
        """Test creating price with float amount."""
        price = TrackingPrice(amount=129.99, currency="RUB")
        
        assert price.amount == Decimal("129.99")
        assert price.currency == "RUB"

    def test_for_stars_factory(self):
        """Test factory method for Stars."""
        price = TrackingPrice.for_stars()
        
        assert price.amount == Decimal("576")
        assert price.currency == "XTR"

    def test_for_rubles_factory(self):
        """Test factory method for Rubles."""
        price = TrackingPrice.for_rubles()
        
        assert price.amount == Decimal("129.00")
        assert price.currency == "RUB"

    def test_invalid_currency(self):
        """Test creating price with invalid currency."""
        with pytest.raises(ValueError, match="Currency must be one of"):
            TrackingPrice(amount=Decimal("100"), currency="EUR")

    def test_negative_amount(self):
        """Test creating price with negative amount."""
        with pytest.raises(ValueError, match="Price cannot be negative"):
            TrackingPrice(amount=Decimal("-100"), currency="RUB")

    def test_invalid_amount_type(self):
        """Test creating price with invalid amount type."""
        with pytest.raises(ValueError, match="Price amount must be numeric"):
            TrackingPrice(amount="invalid", currency="RUB")  # type: ignore

    def test_invalid_currency_type(self):
        """Test creating price with invalid currency type."""
        with pytest.raises(ValueError, match="Currency must be a string"):
            TrackingPrice(amount=Decimal("100"), currency=123)  # type: ignore

    def test_str_representation_stars(self):
        """Test string representation for Stars."""
        price = TrackingPrice.for_stars()
        
        assert str(price) == "576 ⭐"

    def test_str_representation_rub(self):
        """Test string representation for Rubles."""
        price = TrackingPrice.for_rubles()
        
        assert str(price) == "129.00 RUB"

    def test_immutability(self):
        """Test that price is immutable."""
        price = TrackingPrice.for_stars()
        
        with pytest.raises(Exception):  # FrozenInstanceError
            price.amount = Decimal("999")  # type: ignore

    def test_equality(self):
        """Test price equality."""
        price1 = TrackingPrice(amount=Decimal("129"), currency="RUB")
        price2 = TrackingPrice(amount=Decimal("129"), currency="RUB")
        price3 = TrackingPrice(amount=Decimal("130"), currency="RUB")
        
        assert price1 == price2
        assert price1 != price3
