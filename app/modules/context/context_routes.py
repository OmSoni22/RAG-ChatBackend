from fastapi import APIRouter, Depends, Query, status

from app.core.service_factory import ServiceFactory
from app.core.dependencies import get_service_factory
from .context_schema import ContextBulkCreate, ContextRead, ContextListRead

router = APIRouter()


@router.post("/", response_model=list[ContextRead], status_code=status.HTTP_201_CREATED)
async def add_context(
    payload: ContextBulkCreate,
    factory: ServiceFactory = Depends(get_service_factory),
):
    """
    Add one or more context chunks in a single request.

    Send an **items** array where each element has `title`, `content`,
    and an optional `metadata_` dict. Each item is embedded using
    Google text-embedding-004 and stored in the database.

    Example payload:
    ```json
    {
      "items": [
        {"title": "Doc A", "content": "..."},
        {"title": "Doc B", "content": "...", "metadata_": {"source": "web"}}
      ]
    }
    ```
    """
    return await factory.context.add_contexts_bulk(payload)


@router.get("/", response_model=ContextListRead)
async def list_contexts(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Items per page"),
    factory: ServiceFactory = Depends(get_service_factory),
):
    """
    List all stored context items with pagination.
    """
    return await factory.context.list_contexts(page=page, size=size)


@router.get("/{item_id}", response_model=ContextRead)
async def get_context(
    item_id: int,
    factory: ServiceFactory = Depends(get_service_factory),
):
    """
    Retrieve a single context item by ID.
    """
    return await factory.context.get_context(item_id)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_context(
    item_id: int,
    factory: ServiceFactory = Depends(get_service_factory),
):
    """
    Delete a context item by ID.
    """
    await factory.context.delete_context(item_id)
