from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.settings import settings
from app.modules.context.context_model import ContextItem
from app.modules.context.context_schema import ContextCreate


class ContextRepository:
    """Handles all database operations for ContextItem."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: ContextCreate, embedding: list[float]) -> ContextItem:
        """Insert a new context item with its embedding."""
        item = ContextItem(
            title=data.title,
            content=data.content,
            embedding=embedding,
            metadata_=data.metadata_,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_by_id(self, item_id: int) -> ContextItem | None:
        """Fetch a single context item by primary key."""
        result = await self.session.execute(
            select(ContextItem).where(ContextItem.id == item_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, page: int = 1, size: int = 50) -> tuple[list[ContextItem], int]:
        """Fetch paginated context items, returns (items, total_count)."""
        offset = (page - 1) * size

        count_result = await self.session.execute(
            select(func.count()).select_from(ContextItem)
        )
        total = count_result.scalar_one()

        result = await self.session.execute(
            select(ContextItem)
            .order_by(ContextItem.created_at.desc())
            .offset(offset)
            .limit(size)
        )
        items = list(result.scalars().all())
        return items, total

    async def delete(self, item: ContextItem) -> None:
        """Delete a context item."""
        await self.session.delete(item)
        await self.session.flush()

    async def find_similar(
        self, query_vector: list[float], top_k: int = 5
    ) -> list[ContextItem]:
        """
        Retrieve the top-k most similar context items using cosine distance.

        Uses the HNSW index on (embedding::halfvec(3072)) for fast ANN search.
        The query vector is cast to halfvec to match the index expression.
        """
        # Cast both the column and the query literal to halfvec so Postgres
        # uses the HNSW index instead of falling back to a sequential scan.
        dims = settings.embedding_dims
        query_vector_literal = f"'[{','.join(str(v) for v in query_vector)}]'::halfvec({dims})"
        order_expr = text(
            f"embedding::halfvec({dims}) <=> {query_vector_literal}"
        )
        result = await self.session.execute(
            select(ContextItem)
            .order_by(order_expr)
            .limit(top_k)
        )
        return list(result.scalars().all())
