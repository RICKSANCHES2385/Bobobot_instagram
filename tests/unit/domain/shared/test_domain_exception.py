"""Tests for DomainException."""
import pytest
from src.domain.shared.exceptions.base import DomainException


class TestException(DomainException):
    """Test exception."""
    pass


def test_domain_exception_has_message():
    """Domain exception should have a message."""
    exc = DomainException("Test error")
    
    assert exc.message == "Test error"
    assert str(exc) == "Test error"


def test_domain_exception_has_code():
    """Domain exception should have a code."""
    exc1 = DomainException("Test error", code="TEST_ERROR")
    exc2 = TestException("Test error")
    
    assert exc1.code == "TEST_ERROR"
    assert exc2.code == "TestException"  # Defaults to class name


def test_domain_exception_can_be_raised():
    """Domain exception should be raisable."""
    with pytest.raises(DomainException) as exc_info:
        raise DomainException("Test error", code="TEST")
    
    assert exc_info.value.message == "Test error"
    assert exc_info.value.code == "TEST"
