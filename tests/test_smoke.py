"""Smoke test to verify test infrastructure."""


def test_smoke():
    """Basic smoke test."""
    assert True


def test_imports():
    """Test that we can import from src."""
    import src
    
    assert src is not None


def test_python_version():
    """Test Python version is 3.11+."""
    import sys
    
    assert sys.version_info >= (3, 11), "Python 3.11+ is required"


def test_pytest_working():
    """Test that pytest is working correctly."""
    assert 1 + 1 == 2
