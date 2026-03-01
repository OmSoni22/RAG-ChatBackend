from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any


class ServiceFactory:
    """
    Factory to manage service instantiation and dependency injection.
    Scope: Per Request.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self._services: Dict[str, Any] = {}

    @property
    def cache(self) -> "CacheService":
        """Get or create CacheService."""
        if "cache" not in self._services:
            from app.core.cache.cache_service import CacheService
            self._services["cache"] = CacheService()
        return self._services["cache"]

    @property
    def context(self) -> "ContextService":
        """Get or create ContextService."""
        if "context" not in self._services:
            from app.modules.context.services.context_service import ContextService
            self._services["context"] = ContextService(session=self.session)
        return self._services["context"]

    @property
    def chat(self) -> "ChatService":
        """Get or create ChatService."""
        if "chat" not in self._services:
            from app.modules.chat.services.chat_service import ChatService
            self._services["chat"] = ChatService(
                session=self.session,
                context_service=self.context,
            )
        return self._services["chat"]
