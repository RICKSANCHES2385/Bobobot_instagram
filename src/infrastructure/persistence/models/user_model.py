"""User SQLAlchemy Model."""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from src.infrastructure.persistence.base import Base


class UserRoleDB(str, enum.Enum):
    """User role enum for database."""
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"


class SubscriptionStatusDB(str, enum.Enum):
    """Subscription status enum for database."""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    TRIAL = "trial"


class UserModel(Base):
    """User database model."""

    __tablename__ = "users"

    id = Column(String(20), primary_key=True)
    telegram_username = Column(String(32), nullable=True, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    role = Column(SQLEnum(UserRoleDB), nullable=False, default=UserRoleDB.USER)
    subscription_status = Column(
        SQLEnum(SubscriptionStatusDB),
        nullable=False,
        default=SubscriptionStatusDB.EXPIRED,
    )
    subscription_expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    last_activity_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscriptions = relationship("SubscriptionModel", back_populates="user")
    payments = relationship("PaymentModel", back_populates="user")
    referral = relationship(
        "ReferralModel",
        foreign_keys="ReferralModel.referrer_user_id",
        back_populates="referrer",
        uselist=False,
    )
    referred_by = relationship(
        "ReferralModel",
        foreign_keys="ReferralModel.referred_user_id",
        back_populates="referred_user",
        uselist=False,
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<User(id={self.id}, username={self.telegram_username})>"
