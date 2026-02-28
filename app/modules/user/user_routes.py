from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.service_factory import ServiceFactory
from app.core.dependencies import get_service_factory
from .user_schema import UserCreate, UserRead

router = APIRouter()


@router.post("/", response_model=UserRead, status_code=201)
async def create_user(
    payload: UserCreate,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """
    Create a new user.
    
    - **name**: User name (required)
    - **description**: User description (optional)
    """
    return await factory.user.create_user(payload)


@router.get("/", response_model=List[UserRead])
async def list_users(factory: ServiceFactory = Depends(get_service_factory)):
    """
    List all users.
    
    Returns a list of all users in the database.
    """
    return await factory.user.get_users()
