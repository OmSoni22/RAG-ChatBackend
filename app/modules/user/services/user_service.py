from sqlalchemy.ext.asyncio import AsyncSession
from ..user_repository import UserRepository
from ..user_model import User
from ..user_schema import UserCreate
# Note: We don't import NotificationService type here to avoid circular imports if it ever happens? 
# Actually we can import checking TYPE_CHECKING or just import if distinct.
from app.modules.notification.services.notification_service import NotificationService

from app.core.cache.keys import CacheKeys
from app.core.cache.cache_service import CacheService
from app.core.decorators.cached import cached
from ..user_schema import UserRead

class UserService:
    def __init__(self, session: AsyncSession, notification_service: NotificationService, cache_service: CacheService):
        self.repository = UserRepository(session)
        self.notification_service = notification_service
        self.cache_service = cache_service

    async def create_user(self, payload: UserCreate) -> User:
        user = User(**payload.model_dump())
        created_user = await self.repository.create(user)
        
        # Send notification
        await self.notification_service.send_email(
            recipient="admin@example.com",
            subject="New User Created",
            body=f"User '{created_user.name}' was created with ID {created_user.id}"
        )
        
        # Invalidate cache
        await self.cache_service.delete(CacheKeys.USER_LIST)
        
        return created_user

    @cached(key_builder=lambda *args, **kwargs: CacheKeys.USER_LIST, model=UserRead)
    async def get_users(self):
        users = await self.repository.get_all()
        return [UserRead.model_validate(u) for u in users]
