from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Any
from app.core.service_factory import ServiceFactory
from app.core.dependencies import get_service_factory

router = APIRouter()

@router.get("/", summary="Get cache value or list keys")
async def get_cache(
    key: Optional[str] = Query(None, description="Cache key to retrieve. If omitted, lists all keys."),
    factory: ServiceFactory = Depends(get_service_factory)
):
    """
    Retrieve a value from the cache by key.
    If no key is provided, returns a list of all cache keys.
    """
    if key:
        value = await factory.cache.get(key)
        if value is None:
            raise HTTPException(status_code=404, detail="Cache key not found")
        return {"key": key, "value": value}
    
    # List all keys if no key provided
    keys = await factory.cache.list_keys()
    return {"keys": keys}


@router.delete("/{key}", summary="Delete a cache key")
async def delete_cache(
    key: str,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """
    Delete a specific key from the cache.
    """
    await factory.cache.delete(key)
    return {"message": f"Cache key '{key}' deleted"}
