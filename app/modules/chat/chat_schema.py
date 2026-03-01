from datetime import datetime
from pydantic import BaseModel, ConfigDict


# ─── Thread schemas ───────────────────────────────────────────────────────────

class ThreadCreate(BaseModel):
    """Schema for creating a new chat thread."""
    title: str
    description: str | None = None


class ThreadRead(BaseModel):
    """Schema for reading a chat thread."""
    id: int
    title: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ThreadListRead(BaseModel):
    """Paginated thread list response."""
    items: list[ThreadRead]
    total: int
    page: int
    size: int


# ─── Message schemas ──────────────────────────────────────────────────────────

class MessageCreate(BaseModel):
    """Schema for sending a new user message."""
    content: str


class MessageRead(BaseModel):
    """Schema for reading a single chat message."""
    id: int
    thread_id: int
    role: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageHistoryRead(BaseModel):
    """Full message history for a thread."""
    thread_id: int
    messages: list[MessageRead]
