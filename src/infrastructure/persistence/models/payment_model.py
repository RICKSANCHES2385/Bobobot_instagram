"""Payment SQLAlchemy model."""
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from ..base import Base


class PaymentModel(Base):
    """Payment database model."""
    
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(20), ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False)
    method = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, index=True)
    transaction_id = Column(String(255), nullable=True, unique=True, index=True)
    failure_reason = Column(String(500), nullable=True)
    refund_amount = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("UserModel", back_populates="payments")
    
    def __repr__(self):
        """String representation."""
        return f"<PaymentModel(id={self.id}, user_id={self.user_id}, status={self.status})>"
