"""Tests for Register User Use Case."""

import pytest
from unittest.mock import AsyncMock

from src.application.user_management.use_cases.register_user import RegisterUserUseCase
from src.application.user_management.dtos.user_dto import RegisterUserDTO


@pytest.fixture
def mock_user_repository():
    """Create mock user repository."""
    return AsyncMock()


@pytest.fixture
def use_case(mock_user_repository):
    """Create use case instance."""
    return RegisterUserUseCase(mock_user_repository)


@pytest.mark.asyncio
class TestRegisterUserUseCase:
    """Test register user use case."""

    async def test_register_new_user(self, use_case, mock_user_repository):
        """Test registering new user."""
        # Arrange
        dto = RegisterUserDTO(
            user_id="123456789",
            telegram_username="test_user",
            first_name="John",
            last_name="Doe",
        )
        mock_user_repository.exists.return_value = False

        # Act
        result = await use_case.execute(dto)

        # Assert
        assert result.user_id == "123456789"
        assert result.telegram_username == "test_user"
        assert result.first_name == "John"
        assert result.last_name == "Doe"
        assert result.role == "user"
        mock_user_repository.save.assert_called_once()

    async def test_register_user_already_exists(self, use_case, mock_user_repository):
        """Test registering user that already exists."""
        # Arrange
        dto = RegisterUserDTO(
            user_id="123456789",
            telegram_username="test_user",
        )
        mock_user_repository.exists.return_value = True

        # Act & Assert
        with pytest.raises(ValueError, match="already exists"):
            await use_case.execute(dto)

        mock_user_repository.save.assert_not_called()

    async def test_register_user_without_username(self, use_case, mock_user_repository):
        """Test registering user without username."""
        # Arrange
        dto = RegisterUserDTO(
            user_id="123456789",
            first_name="John",
        )
        mock_user_repository.exists.return_value = False

        # Act
        result = await use_case.execute(dto)

        # Assert
        assert result.user_id == "123456789"
        assert result.telegram_username is None
        assert result.first_name == "John"
        mock_user_repository.save.assert_called_once()
