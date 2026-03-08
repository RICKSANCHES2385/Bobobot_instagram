"""Tests for BaseValueObject."""
import pytest
from dataclasses import dataclass
from src.domain.shared.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class TestVO(BaseValueObject):
    """Test value object."""
    value: int
    
    def _validate(self) -> None:
        if self.value < 0:
            raise ValueError("Value must be non-negative")


def test_value_object_is_immutable():
    """Value object should be immutable."""
    vo = TestVO(value=10)
    
    with pytest.raises(Exception):  # FrozenInstanceError
        vo.value = 20  # type: ignore


def test_value_object_equality_by_value():
    """Value objects with same values should be equal."""
    vo1 = TestVO(value=10)
    vo2 = TestVO(value=10)
    vo3 = TestVO(value=20)
    
    assert vo1 == vo2
    assert vo1 != vo3


def test_value_object_hash():
    """Value objects should be hashable."""
    vo1 = TestVO(value=10)
    vo2 = TestVO(value=10)
    
    assert hash(vo1) == hash(vo2)
    assert {vo1, vo2} == {vo1}  # Same hash, same set element


def test_value_object_validation():
    """Value object should validate on creation."""
    with pytest.raises(ValueError, match="Value must be non-negative"):
        TestVO(value=-1)
