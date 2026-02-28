"""
Unit tests for User service.

These tests verify the business logic in isolation.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.user.user_model import User
from app.modules.user.user_schema import UserCreate
from app.modules.user.services.user_service import UserService


class DummyNotificationService:
    async def send_email(self, recipient: str, subject: str, body: str):
        # No-op for tests
        return None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_user(test_db: AsyncSession, sample_user_data: dict):
    """Test creating a user."""
    # Arrange
    service = UserService(test_db, DummyNotificationService())
    payload = UserCreate(**sample_user_data)
    
    # Act
    result = await service.create_user(payload)
    await test_db.commit()
    
    # Assert
    assert result is not None
    assert isinstance(result, User)
    assert result.name == sample_user_data["name"]
    assert result.description == sample_user_data["description"]
    assert result.id is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_users(test_db: AsyncSession, sample_user_data: dict):
    """Test retrieving all users."""
    # Arrange
    service = UserService(test_db, DummyNotificationService())
    
    # Create test users
    user1 = UserCreate(**sample_user_data)
    user2 = UserCreate(name="Another User", description="Another test user")
    
await service.create_user(user1)
    await service.create_user(user2)
    await test_db.commit()
    
    # Act
    results = await service.get_users()
    
    # Assert
    assert len(results) == 2
    assert all(isinstance(u, User) for u in results)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_user_minimal(test_db: AsyncSession):
    """Test creating a user with minimal data."""
    # Arrange
    service = UserService(test_db, DummyNotificationService())
    payload = UserCreate(name="Minimal User")
    
    # Act
    result = await service.create_user(payload)
    await test_db.commit()
    
    # Assert
    assert result.name == "Minimal User"
    assert result.description is None
