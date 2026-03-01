from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Any


class ContextCreate(BaseModel):
    """Schema for creating a new context item."""

    title: str
    content: str
    metadata_: dict[str, Any] | None = None

    model_config = ConfigDict(populate_by_name=True)


class ContextRead(BaseModel):
    """Schema for reading a context item (embedding is never exposed)."""

    id: int
    title: str
    content: str
    metadata_: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContextListRead(BaseModel):
    """Paginated context list response."""

    items: list[ContextRead]
    total: int
    page: int
    size: int
