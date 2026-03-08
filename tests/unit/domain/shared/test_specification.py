"""Tests for Specification Pattern."""
import pytest
from dataclasses import dataclass
from src.domain.shared.specifications.base import Specification


@dataclass
class User:
    """Test user class."""
    age: int
    is_active: bool


class AgeSpecification(Specification):
    """Specification for user age."""
    
    def __init__(self, min_age: int):
        self.min_age = min_age
    
    def is_satisfied_by(self, candidate: User) -> bool:
        return candidate.age >= self.min_age


class ActiveSpecification(Specification):
    """Specification for active users."""
    
    def is_satisfied_by(self, candidate: User) -> bool:
        return candidate.is_active


def test_specification_simple():
    """Specification should check if candidate satisfies condition."""
    spec = AgeSpecification(min_age=18)
    
    user1 = User(age=20, is_active=True)
    user2 = User(age=16, is_active=True)
    
    assert spec.is_satisfied_by(user1)
    assert not spec.is_satisfied_by(user2)


def test_specification_and():
    """Specification should support AND combination."""
    age_spec = AgeSpecification(min_age=18)
    active_spec = ActiveSpecification()
    
    combined_spec = age_spec.and_(active_spec)
    
    user1 = User(age=20, is_active=True)  # Both satisfied
    user2 = User(age=20, is_active=False)  # Only age satisfied
    user3 = User(age=16, is_active=True)  # Only active satisfied
    user4 = User(age=16, is_active=False)  # None satisfied
    
    assert combined_spec.is_satisfied_by(user1)
    assert not combined_spec.is_satisfied_by(user2)
    assert not combined_spec.is_satisfied_by(user3)
    assert not combined_spec.is_satisfied_by(user4)


def test_specification_or():
    """Specification should support OR combination."""
    age_spec = AgeSpecification(min_age=18)
    active_spec = ActiveSpecification()
    
    combined_spec = age_spec.or_(active_spec)
    
    user1 = User(age=20, is_active=True)  # Both satisfied
    user2 = User(age=20, is_active=False)  # Only age satisfied
    user3 = User(age=16, is_active=True)  # Only active satisfied
    user4 = User(age=16, is_active=False)  # None satisfied
    
    assert combined_spec.is_satisfied_by(user1)
    assert combined_spec.is_satisfied_by(user2)
    assert combined_spec.is_satisfied_by(user3)
    assert not combined_spec.is_satisfied_by(user4)


def test_specification_not():
    """Specification should support NOT negation."""
    age_spec = AgeSpecification(min_age=18)
    
    negated_spec = age_spec.not_()
    
    user1 = User(age=20, is_active=True)
    user2 = User(age=16, is_active=True)
    
    assert not negated_spec.is_satisfied_by(user1)
    assert negated_spec.is_satisfied_by(user2)


def test_specification_composition():
    """Specification should support complex composition."""
    age_spec = AgeSpecification(min_age=18)
    active_spec = ActiveSpecification()
    
    # (age >= 18 AND active) OR NOT active
    complex_spec = age_spec.and_(active_spec).or_(active_spec.not_())
    
    user1 = User(age=20, is_active=True)  # Satisfies first part
    user2 = User(age=16, is_active=False)  # Satisfies second part
    user3 = User(age=16, is_active=True)  # Satisfies neither
    
    assert complex_spec.is_satisfied_by(user1)
    assert complex_spec.is_satisfied_by(user2)
    assert not complex_spec.is_satisfied_by(user3)
