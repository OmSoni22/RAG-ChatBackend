from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.chat.chat_model import ChatThread, ChatMessage
from app.modules.chat.chat_schema import ThreadCreate, MessageCreate


class ChatRepository:
    """Handles all database operations for ChatThread and ChatMessage."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ─── Thread operations ────────────────────────────────────────────────────

    async def create_thread(self, data: ThreadCreate) -> ChatThread:
        """Create a new chat thread."""
        thread = ChatThread(title=data.title, description=data.description)
        self.session.add(thread)
        await self.session.flush()
        await self.session.refresh(thread)
        return thread

    async def get_thread_by_id(self, thread_id: int) -> ChatThread | None:
        """Fetch a single thread by primary key."""
        result = await self.session.execute(
            select(ChatThread).where(ChatThread.id == thread_id)
        )
        return result.scalar_one_or_none()

    async def get_all_threads(
        self, page: int = 1, size: int = 50
    ) -> tuple[list[ChatThread], int]:
        """Fetch paginated threads, returns (items, total_count)."""
        offset = (page - 1) * size

        count_result = await self.session.execute(
            select(func.count()).select_from(ChatThread)
        )
        total = count_result.scalar_one()

        result = await self.session.execute(
            select(ChatThread)
            .order_by(ChatThread.updated_at.desc())
            .offset(offset)
            .limit(size)
        )
        return list(result.scalars().all()), total

    async def delete_thread(self, thread: ChatThread) -> None:
        """Delete a thread (cascades to messages via DB constraint)."""
        await self.session.delete(thread)
        await self.session.flush()

    # ─── Message operations ───────────────────────────────────────────────────

    async def create_message(
        self, thread_id: int, role: str, content: str
    ) -> ChatMessage:
        """Persist a single message to a thread."""
        msg = ChatMessage(thread_id=thread_id, role=role, content=content)
        self.session.add(msg)
        await self.session.flush()
        await self.session.refresh(msg)
        return msg

    async def get_messages_by_thread(self, thread_id: int) -> list[ChatMessage]:
        """Fetch full message history for a thread in chronological order."""
        result = await self.session.execute(
            select(ChatMessage)
            .where(ChatMessage.thread_id == thread_id)
            .order_by(ChatMessage.created_at.asc())
        )
        return list(result.scalars().all())
