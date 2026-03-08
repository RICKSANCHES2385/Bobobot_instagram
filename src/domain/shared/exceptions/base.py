"""Base Domain Exception for DDD."""


class DomainException(Exception):
    """Base class for Domain Exceptions.
    
    Domain exceptions represent business rule violations
    or invalid domain operations.
    """
    
    def __init__(self, message: str, code: str | None = None):
        """Initialize domain exception.
        
        Args:
            message: Human-readable error message.
            code: Error code (defaults to class name).
        """
        self.message = message
        self.code = code or self.__class__.__name__
        super().__init__(self.message)
