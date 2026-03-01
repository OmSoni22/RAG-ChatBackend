import asyncio
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse

from app.core.service_factory import ServiceFactory
from app.core.dependencies import get_service_factory
from .chat_schema import (
    ThreadCreate,
    ThreadRead,
    ThreadListRead,
    MessageCreate,
    MessageHistoryRead,
)

router = APIRouter()


# ─── Thread endpoints ─────────────────────────────────────────────────────────

@router.post("/threads", response_model=ThreadRead, status_code=status.HTTP_201_CREATED)
async def create_thread(
    payload: ThreadCreate,
    factory: ServiceFactory = Depends(get_service_factory),
):
    """
    Create a new chat thread.
    """
    return await factory.chat.create_thread(payload)


@router.get("/threads", response_model=ThreadListRead)
async def list_threads(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Items per page"),
    factory: ServiceFactory = Depends(get_service_factory),
):
    """
    List all chat threads with pagination.
    """
    return await factory.chat.list_threads(page=page, size=size)


@router.get("/threads/{thread_id}", response_model=ThreadRead)
async def get_thread(
    thread_id: int,
    factory: ServiceFactory = Depends(get_service_factory),
):
    """
    Retrieve a single chat thread by ID.
    """
    return await factory.chat.get_thread(thread_id)


@router.delete("/threads/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_thread(
    thread_id: int,
    factory: ServiceFactory = Depends(get_service_factory),
):
    """
    Delete a thread and all its messages.
    """
    await factory.chat.delete_thread(thread_id)


# ─── Message endpoints ────────────────────────────────────────────────────────

@router.get("/threads/{thread_id}/messages", response_model=MessageHistoryRead)
async def get_messages(
    thread_id: int,
    factory: ServiceFactory = Depends(get_service_factory),
):
    """
    Get the full message history for a chat thread in chronological order.
    """
    return await factory.chat.get_history(thread_id)


@router.post("/threads/{thread_id}/messages", status_code=status.HTTP_200_OK)
async def send_message(
    thread_id: int,
    payload: MessageCreate,
    factory: ServiceFactory = Depends(get_service_factory),
):
    """
    Send a user message and receive a **streaming** RAG-powered response.

    The response is a Server-Sent Events (SSE) stream.
    Each event carries a JSON delta:

    ```
    data: {"delta": "partial answer text"}
    data: [DONE]
    ```

    The user message and the complete assistant reply are both persisted to the DB.
    """
    return StreamingResponse(
        factory.chat.stream_response(thread_id, payload.content),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disables Nginx buffering for SSE
        },
    )
