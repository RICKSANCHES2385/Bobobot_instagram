"""Tests for ContentTracking Aggregate."""

import pytest
from datetime import datetime, timedelta

from src.domain.content_tracking.aggregates.content_tracking import ContentTracking
from src.domain.content_tracking.value_objects.tracking_id import TrackingId
from src.domain.content_tracking.value_objects.tracking_status import TrackingStatus, TrackingStatusEnum
from src.domain.content_tracking.value_objects.content_type import ContentType, ContentTypeEnum
from src.domain.content_tracking.value_objects.check_interval import CheckInterval
from src.domain.instagram_integration.value_objects.instagram_user_id import InstagramUserId
from src.domain.instagram_integration.value_objects.instagram_username import InstagramUsername


def test_create_content_tracking():
    """Test creating content tracking."""
    tracking = ContentTracking.create(
        tracking_id=TrackingId("track_123"),
        user_id="user_456",
        instagram_user_id=InstagramUserId("789"),
        instagram_username=InstagramUsername("testuser"),
        content_type=ContentType(ContentTypeEnum.STORIES),
        check_interval=CheckInterval(30),
    )

    assert tracking.tracking_id.value == "track_123"
    assert tracking.user_id == "user_456"
    assert tracking.instagram_user_id.value == "789"
    assert tracking.instagram_username.value == "testuser"
    assert tracking.content_type.is_stories()
    assert tracking.status.is_active()
    assert tracking.check_interval.minutes == 30
    assert tracking.notification_enabled is True
    assert len(tracking.domain_events) == 1


def test_pause_tracking():
    """Test pausing tracking."""
    tracking = ContentTracking.create(
        tracking_id=TrackingId("track_123"),
        user_id="user_456",
        instagram_user_id=InstagramUserId("789"),
        instagram_username=InstagramUsername("testuser"),
        content_type=ContentType(ContentTypeEnum.POSTS),
        check_interval=CheckInterval(60),
    )

    tracking.pause()

    assert tracking.status.is_paused()
    assert len(tracking.domain_events) == 2


def test_stop_tracking():
    """Test stopping tracking."""
    tracking = ContentTracking.create(
        tracking_id=TrackingId("track_123"),
        user_id="user_456",
        instagram_user_id=InstagramUserId("789"),
        instagram_username=InstagramUsername("testuser"),
        content_type=ContentType(ContentTypeEnum.POSTS),
        check_interval=CheckInterval(60),
    )

    tracking.stop()

    assert tracking.status.is_stopped()
    assert len(tracking.domain_events) == 2


def test_detect_new_content():
    """Test detecting new content."""
    tracking = ContentTracking.create(
        tracking_id=TrackingId("track_123"),
        user_id="user_456",
        instagram_user_id=InstagramUserId("789"),
        instagram_username=InstagramUsername("testuser"),
        content_type=ContentType(ContentTypeEnum.POSTS),
        check_interval=CheckInterval(60),
    )

    tracking.detect_new_content("post_456", "https://instagram.com/p/456")

    assert tracking.last_content_id == "post_456"
    assert tracking.last_check_at is not None
    assert len(tracking.domain_events) == 2


def test_should_check_now_first_time():
    """Test should check now on first check."""
    tracking = ContentTracking.create(
        tracking_id=TrackingId("track_123"),
        user_id="user_456",
        instagram_user_id=InstagramUserId("789"),
        instagram_username=InstagramUsername("testuser"),
        content_type=ContentType(ContentTypeEnum.POSTS),
        check_interval=CheckInterval(60),
    )

    assert tracking.should_check_now() is True
