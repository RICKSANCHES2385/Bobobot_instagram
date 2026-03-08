"""Content Tracking SQLAlchemy Model."""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from src.infrastructure.persistence.base import Base


class TrackingStatusDB(str, enum.Enum):
    """Tracking status enum for database."""
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"


class ContentTypeDB(str, enum.Enum):
    """Content type enum for database."""
    POSTS = "posts"
    STORIES = "stories"
    REELS = "reels"
    HIGHLIGHTS = "highlights"


class ContentTrackingModel(Base):
    """Content tracking database model."""

    __tablename__ = "content_trackings"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(50), nullable=False, index=True)
    instagram_user_id = Column(String(50), nullable=False, index=True)
    instagram_username = Column(String(100), nullable=False)
    content_type = Column(SQLEnum(ContentTypeDB), nullable=False)
    status = Column(SQLEnum(TrackingStatusDB), nullable=False, default=TrackingStatusDB.ACTIVE)
    check_interval_minutes = Column(Integer, nullable=False)
    last_check_at = Column(DateTime, nullable=True)
    last_content_id = Column(String(100), nullable=True)
    notification_enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation."""
        return f"<ContentTracking(id={self.id}, user={self.user_id}, instagram={self.instagram_username})>"
