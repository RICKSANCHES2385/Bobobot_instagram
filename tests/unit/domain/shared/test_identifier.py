"""Tests for Identifier."""
import pytest
from uuid import UUID, uuid4
from src.domain.shared.value_objects.identifier import Identifier


def test_identifier_with_int():
    """Identifier should work with int values."""
    id1 = Identifier[int](value=123)
    id2 = Identifier[int](value=123)
    id3 = Identifier[int](value=456)
    
    assert id1 == id2
    assert id1 != id3
    assert int(id1) == 123
    assert str(id1) == "123"


def test_identifier_with_str():
    """Identifier should work with str values."""
    id1 = Identifier[str](value="abc")
    id2 = Identifier[str](value="abc")
    id3 = Identifier[str](value="def")
    
    assert id1 == id2
    assert id1 != id3
    assert str(id1) == "abc"


def test_identifier_with_uuid():
    """Identifier should work with UUID values."""
    uuid_val = uuid4()
    id1 = Identifier[UUID](value=uuid_val)
    id2 = Identifier[UUID](value=uuid_val)
    id3 = Identifier[UUID](value=uuid4())
    
    assert id1 == id2
    assert id1 != id3
    assert str(id1) == str(uuid_val)


def test_identifier_validates_none():
    """Identifier should not accept None values."""
    with pytest.raises(ValueError, match="Identifier value cannot be None"):
        Identifier[int](value=None)  # type: ignore


def test_identifier_int_conversion_fails_for_non_int():
    """Int conversion should fail for non-int identifiers."""
    id_str = Identifier[str](value="abc")
    
    with pytest.raises(TypeError, match="Cannot convert"):
        int(id_str)
