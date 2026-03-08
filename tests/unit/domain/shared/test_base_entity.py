"""Tests for BaseEntity."""
import pytest
from dataclasses import dataclass
from datetime import datetime
import time
from src.domain.shared.entities.base import BaseEntity


@dataclass(eq=False)
class TestEntity(BaseEntity):
    """Test entity."""
    name: str = "test"


def test_entity_equality_by_id():
    """Entities with same ID should be equal."""
    entity1 = TestEntity(id=1, name="Alice")
    entity2 = TestEntity(id=1, name="Bob")
    entity3 = TestEntity(id=2, name="Alice")
    
    assert entity1 == entity2  # Same ID, different name
    assert entity1 != entity3  # Different ID


def test_entity_hash_by_id():
    """Entities should be hashable by ID."""
    entity1 = TestEntity(id=1, name="Alice")
    entity2 = TestEntity(id=1, name="Bob")
    
    assert hash(entity1) == hash(entity2)
    assert {entity1, entity2} == {entity1}


def test_entity_timestamps():
    """Entity should have creation and update timestamps."""
    entity = TestEntity(id=1)
    
    assert isinstance(entity.created_at, datetime)
    assert isinstance(entity.updated_at, datetime)
    assert entity.created_at == entity.updated_at


def test_entity_touch_updates_timestamp():
    """Touch should update the updated_at timestamp."""
    entity = TestEntity(id=1)
    original_updated_at = entity.updated_at
    
    time.sleep(0.01)  # Small delay
    entity._touch()
    
    assert entity.updated_at > original_updated_at
    assert entity.created_at < entity.updated_at
