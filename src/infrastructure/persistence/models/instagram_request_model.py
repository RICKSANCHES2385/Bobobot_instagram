"""SQLAlchemy model for Instagram requests."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class InstagramRequestModel(Base):
    """Instagram request model for logging API requests."""
    
    __tablename__ = "instagram_requests"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    request_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_username: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    response_time_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True
    )
    
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
        Index('idx_user_type', 'user_id', 'request_type'),
        Index('idx_status', 'status'),
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<InstagramRequest(id={self.id}, "
            f"user_id={self.user_id}, "
            f"type={self.request_type}, "
            f"status={self.status})>"
        )
