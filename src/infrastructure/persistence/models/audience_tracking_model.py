"""Audience Tracking SQLAlchemy Model."""

from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.base import Base


class AudienceTrackingModel(Base):
    """Audience tracking subscription database model."""

    __tablename__ = "audience_tracking_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # User who owns this subscription
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    
    # Target Instagram account being tracked
    target_username: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    target_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Subscription status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Payment information
    payment_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    amount_paid: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    
    # Tracking data
    last_follower_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_following_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<AudienceTrackingModel("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"target=@{self.target_username}, "
            f"active={self.is_active}"
            f")>"
        )
