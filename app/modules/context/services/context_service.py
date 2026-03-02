import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.context.context_model import ContextItem
from app.modules.context.context_repository import ContextRepository
from app.modules.context.context_schema import ContextCreate, ContextBulkCreate, ContextRead, ContextListRead
from app.core.embeddings import get_embedding, get_query_embedding
from app.core.config.settings import settings
from app.core.exceptions.base import AppException
from app.core.logging.logger import add_to_log


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
        add_to_log(
            "debug",
            f"[CONTEXT] Generating embedding for new context item | "
            f"content_length={len(data.content)} chars | "
            f"text_preview={data.content[:120]!r}",
        )
        embedding = await get_embedding(data.content)
        item = await self.repo.create(data, embedding)
        return ContextRead.model_validate(item)

    async def add_contexts_bulk(self, bulk: ContextBulkCreate) -> list[ContextRead]:
        """
        Embed and persist multiple context items.

        Embeddings are fetched concurrently (network-bound, no shared state),
        then each item is saved to the DB one-by-one so the session never
        has to flush concurrently (which SQLAlchemy does not support).
        """
        add_to_log(
            "debug",
            f"[CONTEXT] Bulk ingestion started | count={len(bulk.items)} items",
        )

        # --- Step 1: fetch all embeddings in parallel (safe) ---
        async def _embed(data: ContextCreate) -> tuple[ContextCreate, list[float]]:
            add_to_log(
                "debug",
                f"[CONTEXT] Generating embedding | "
                f"title={data.title!r} | "
                f"content_length={len(data.content)} chars",
            )
            embedding = await get_embedding(data.content)
            return data, embedding

        pairs = await asyncio.gather(*[_embed(item) for item in bulk.items])

        # --- Step 2: save to DB sequentially (one flush at a time) ---
        results: list[ContextRead] = []
        for data, embedding in pairs:
            item = await self.repo.create(data, embedding)
            results.append(ContextRead.model_validate(item))

        add_to_log(
            "debug",
            f"[CONTEXT] Bulk ingestion complete | saved={len(results)} items",
        )
        return results

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
        add_to_log(
            "debug",
            f"[CONTEXT] Generating query embedding for similarity search | "
            f"query={query_text!r}",
        )
        query_vector = await get_query_embedding(query_text)
        results = await self.repo.find_similar(query_vector, top_k=settings.top_k_context)
        add_to_log(
            "debug",
            f"[CONTEXT] Top-K context chunks retrieved | "
            f"top_k={settings.top_k_context} | "
            f"returned={len(results)} chunks | "
            + "\n".join(
                f"  [{i + 1}] {chunk.content[:100]!r}"
                for i, chunk in enumerate(results)
            ),
        )
        return results
