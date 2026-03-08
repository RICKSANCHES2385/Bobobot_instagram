"""Notification SQLAlchemy Model."""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, Enum as SQLEnum, JSON
import enum

from src.infrastructure.persistence.base import Base


class NotificationTypeDB(str, enum.Enum):
    """Notification type enum for database."""
    CONTENT_UPDATE = "content_update"
    SUBSCRIPTION_EXPIRING = "subscription_expiring"
    SUBSCRIPTION_EXPIRED = "subscription_expired"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    SYSTEM_MESSAGE = "system_message"


class NotificationStatusDB(str, enum.Enum):
    """Notification status enum for database."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationPriorityDB(str, enum.Enum):
    """Notification priority enum for database."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationModel(Base):
    """Notification database model."""

    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(50), nullable=False, index=True)
    notification_type = Column(SQLEnum(NotificationTypeDB), nullable=False)
    status = Column(SQLEnum(NotificationStatusDB), nullable=False, default=NotificationStatusDB.PENDING, index=True)
    priority = Column(SQLEnum(NotificationPriorityDB), nullable=False, default=NotificationPriorityDB.NORMAL)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSON, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    max_retries = Column(Integer, nullable=False, default=3)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation."""
        return f"<Notification(id={self.id}, user={self.user_id}, type={self.notification_type}, status={self.status})>"
