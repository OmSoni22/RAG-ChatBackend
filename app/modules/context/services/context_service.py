from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.context.context_model import ContextItem
from app.modules.context.context_repository import ContextRepository
from app.modules.context.context_schema import ContextCreate, ContextRead, ContextListRead
from app.core.embeddings import get_embedding, get_query_embedding
from app.core.config.settings import settings
from app.core.exceptions.base import AppException


class ContextService:
    """Business logic for context ingestion and retrieval."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ContextRepository(session)

    async def add_context(self, data: ContextCreate) -> ContextRead:
        """
        Embed the provided content and persist the context item.

        Steps:
          1. Generate embedding via Google text-embedding-004.
          2. Save content + embedding to the DB.
          3. Return the created item (without embedding).
        """
        embedding = await get_embedding(data.content)
        item = await self.repo.create(data, embedding)
        return ContextRead.model_validate(item)

    async def get_context(self, item_id: int) -> ContextRead:
        """Fetch a single context item by ID."""
        item = await self.repo.get_by_id(item_id)
        if not item:
            raise AppException(status_code=404, message=f"Context item {item_id} not found")
        return ContextRead.model_validate(item)

    async def list_contexts(self, page: int = 1, size: int = 50) -> ContextListRead:
        """Return a paginated list of context items."""
        items, total = await self.repo.get_all(page=page, size=size)
        return ContextListRead(
            items=[ContextRead.model_validate(i) for i in items],
            total=total,
            page=page,
            size=size,
        )

    async def delete_context(self, item_id: int) -> None:
        """Delete a context item by ID."""
        item = await self.repo.get_by_id(item_id)
        if not item:
            raise AppException(status_code=404, message=f"Context item {item_id} not found")
        await self.repo.delete(item)

    async def find_similar(self, query_text: str) -> list[ContextItem]:
        """
        Retrieve context chunks most relevant to a query string.
        Used internally by the chat service during RAG pipeline.
        """
        query_vector = await get_query_embedding(query_text)
        return await self.repo.find_similar(query_vector, top_k=settings.top_k_context)
