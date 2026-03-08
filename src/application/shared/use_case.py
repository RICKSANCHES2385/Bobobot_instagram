"""Base Use Case."""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

TCommand = TypeVar('TCommand')
TResult = TypeVar('TResult')


class UseCase(ABC, Generic[TCommand, TResult]):
    """Base use case interface."""
    
    @abstractmethod
    async def execute(self, command: TCommand) -> TResult:
        """Execute use case.
        
        Args:
            command: Command to execute.
            
        Returns:
            Result of execution.
        """
        pass
