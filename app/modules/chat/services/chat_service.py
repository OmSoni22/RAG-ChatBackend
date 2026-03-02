import json
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from app.modules.chat.chat_repository import ChatRepository
from app.modules.chat.chat_schema import (
    ThreadCreate,
    ThreadRead,
    ThreadListRead,
    MessageRead,
    MessageHistoryRead,
)
from app.core.config.settings import settings
from app.core.exceptions.base import AppException
from app.core.logging.logger import add_to_log

# Forward reference to avoid circular import
if False:
    from app.modules.context.services.context_service import ContextService

SYSTEM_PROMPT_TEMPLATE = """\
You are a helpful assistant. Use the following retrieved context to answer the user's question.
If the answer cannot be found in the context, say you don't know — do not make things up.

--- CONTEXT START ---
{context}
--- CONTEXT END ---
"""


class ChatService:
    """
    Orchestrates the full RAG pipeline:
      1. Persist the user message.
      2. Embed the user query → retrieve similar context chunks.
      3. Build a prompt = system_prompt(context) + thread history + user message.
      4. Stream the LLM response token-by-token.
      5. Persist the complete assistant message after streaming.
    """

    def __init__(self, session: AsyncSession, context_service: "ContextService"):
        self.session = session
        self.context_service = context_service
        self.repo = ChatRepository(session)
        self._model = GoogleModel(
            settings.llm_model,
            provider=GoogleProvider(api_key=settings.google_api_key),
        )

    # ─── Thread management ────────────────────────────────────────────────────

    async def create_thread(self, data: ThreadCreate) -> ThreadRead:
        """Create a new chat thread."""
        thread = await self.repo.create_thread(data)
        return ThreadRead.model_validate(thread)

    async def get_thread(self, thread_id: int) -> ThreadRead:
        """Fetch a thread by ID."""
        thread = await self.repo.get_thread_by_id(thread_id)
        if not thread:
            raise AppException(status_code=404, message=f"Thread {thread_id} not found")
        return ThreadRead.model_validate(thread)

    async def list_threads(self, page: int = 1, size: int = 50) -> ThreadListRead:
        """Return a paginated list of threads."""
        threads, total = await self.repo.get_all_threads(page=page, size=size)
        return ThreadListRead(
            items=[ThreadRead.model_validate(t) for t in threads],
            total=total,
            page=page,
            size=size,
        )

    async def delete_thread(self, thread_id: int) -> None:
        """Delete a thread and all its messages."""
        thread = await self.repo.get_thread_by_id(thread_id)
        if not thread:
            raise AppException(status_code=404, message=f"Thread {thread_id} not found")
        await self.repo.delete_thread(thread)

    # ─── Message history ──────────────────────────────────────────────────────

    async def get_history(self, thread_id: int) -> MessageHistoryRead:
        """Return full message history for a thread."""
        thread = await self.repo.get_thread_by_id(thread_id)
        if not thread:
            raise AppException(status_code=404, message=f"Thread {thread_id} not found")
        messages = await self.repo.get_messages_by_thread(thread_id)
        return MessageHistoryRead(
            thread_id=thread_id,
            messages=[MessageRead.model_validate(m) for m in messages],
        )

    # ─── RAG Chat (streaming) ─────────────────────────────────────────────────

    async def stream_response(
        self, thread_id: int, user_content: str
    ) -> AsyncIterator[str]:
        """
        Full RAG pipeline yielding SSE-formatted chunks.

        Each yielded string is a complete SSE line ready to be sent to the client:
            "data: {\"delta\": \"token text\"}\\n\\n"

        After all chunks, yields the terminal event:
            "data: [DONE]\\n\\n"

        The user message is persisted before the LLM call.
        The full assistant response is persisted after streaming completes.
        """
        # 1. Validate thread exists
        thread = await self.repo.get_thread_by_id(thread_id)
        if not thread:
            raise AppException(status_code=404, message=f"Thread {thread_id} not found")

        # 2. Persist the user message immediately
        await self.repo.create_message(thread_id, role="user", content=user_content)

        # 3. Retrieve top-k relevant context chunks via cosine similarity
        add_to_log(
            "debug",
            f"[CHAT] Generating query embedding for user prompt | "
            f"thread_id={thread_id} | "
            f"prompt={user_content!r}",
        )
        similar_chunks = await self.context_service.find_similar(user_content)
        context_text = "\n\n".join(
            f"[{i + 1}] {chunk.content}" for i, chunk in enumerate(similar_chunks)
        )

        # 4. Build system prompt with injected context
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            context=context_text if context_text else "No relevant context found."
        )

        # 5. Build conversation history for the LLM
        history_messages = await self.repo.get_messages_by_thread(thread_id)
        add_to_log(
            "debug",
            f"[CHAT] Thread history loaded | "
            f"thread_id={thread_id} | "
            f"total_messages_in_thread={len(history_messages)} "
            f"(excluding current user message: {len(history_messages) - 1})",
        )
        # Build a single string of history (excluding the message we just saved, last item)
        history_text = "\n".join(
            f"{msg.role.upper()}: {msg.content}"
            for msg in history_messages[:-1]  # exclude just-added user message
        )

        # 6. Compose the full prompt
        full_prompt = (
            f"{history_text}\nUSER: {user_content}" if history_text else user_content
        )

        # 7. Stream from PydanticAI and collect full response
        full_response_parts: list[str] = []

        agent = Agent(model=self._model, system_prompt=system_prompt)
        async with agent.run_stream(full_prompt) as result:
            async for delta in result.stream_text(delta=True):
                full_response_parts.append(delta)
                payload = json.dumps({"delta": delta})
                yield f"data: {payload}\n\n"

        # 8. Persist the complete assistant response
        full_response = "".join(full_response_parts)
        await self.repo.create_message(thread_id, role="assistant", content=full_response)

        # 9. Signal end of stream
        yield "data: [DONE]\n\n"
