"""Payment status value object."""
from dataclasses import dataclass
from enum import Enum
from ...shared.value_objects.base import BaseValueObject

class PaymentStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

@dataclass(frozen=True)
class PaymentStatus(BaseValueObject):
    value: PaymentStatusEnum
    
    @staticmethod
    def pending():
        return PaymentStatus(value=PaymentStatusEnum.PENDING)
    
    @staticmethod
    def processing():
        return PaymentStatus(value=PaymentStatusEnum.PROCESSING)
    
    @staticmethod
    def completed():
        return PaymentStatus(value=PaymentStatusEnum.COMPLETED)
    
    @staticmethod
    def failed():
        return PaymentStatus(value=PaymentStatusEnum.FAILED)
    
    @staticmethod
    def cancelled():
        return PaymentStatus(value=PaymentStatusEnum.CANCELLED)
    
    @staticmethod
    def refunded():
        return PaymentStatus(value=PaymentStatusEnum.REFUNDED)
    
    def is_pending(self):
        return self.value == PaymentStatusEnum.PENDING
    
    def is_processing(self):
        return self.value == PaymentStatusEnum.PROCESSING
    
    def is_completed(self):
        return self.value == PaymentStatusEnum.COMPLETED
    
    def is_failed(self):
        return self.value == PaymentStatusEnum.FAILED
    
    def is_cancelled(self):
        return self.value == PaymentStatusEnum.CANCELLED
    
    def is_refunded(self):
        return self.value == PaymentStatusEnum.REFUNDED
    
    def is_final(self):
        return self.value in [
            PaymentStatusEnum.COMPLETED,
            PaymentStatusEnum.FAILED,
            PaymentStatusEnum.CANCELLED,
            PaymentStatusEnum.REFUNDED
        ]
    
    def can_process(self):
        return self.value == PaymentStatusEnum.PENDING
    
    def can_complete(self):
        return self.value == PaymentStatusEnum.PROCESSING
    
    def can_fail(self):
        return self.value in [PaymentStatusEnum.PENDING, PaymentStatusEnum.PROCESSING]
    
    def can_cancel(self):
        return self.value == PaymentStatusEnum.PENDING
    
    def can_refund(self):
        return self.value == PaymentStatusEnum.COMPLETED
