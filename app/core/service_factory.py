from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Type, TypeVar

from app.modules.notification.services.notification_service import NotificationService
from app.modules.user.services.user_service import UserService

class ServiceFactory:
    """
    Factory to manage service instantiation and dependency injection.
    Scope: Per Request.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self._services: Dict[str, Any] = {}

    @property
    def notification(self) -> NotificationService:
        """Get or create NotificationService."""
        if "notification" not in self._services:
            self._services["notification"] = NotificationService()
        return self._services["notification"]

    @property
    def cache(self) -> "CacheService":
        """Get or create CacheService."""
        if "cache" not in self._services:
            from app.core.cache.cache_service import CacheService
            self._services["cache"] = CacheService()
        return self._services["cache"]

    @property
    def user(self) -> UserService:
        """Get or create UserService with dependencies."""
        if "user" not in self._services:
            # Auto-wire dependencies: UserService needs Session + NotificationService + CacheService
            self._services["user"] = UserService(
                session=self.session, 
                notification_service=self.notification,
                cache_service=self.cache
            )
        return self._services["user"]
