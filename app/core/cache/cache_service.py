import json
from typing import Any, Optional, List, Union
from pydantic import BaseModel
from app.core.cache import redis

class CacheService:
    def __init__(self, ttl: int = 300):
        self.default_ttl = ttl

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from the cache."""
        if not redis.redis_client:
            return None
        
        value = await redis.redis_client.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set a value in the cache with serialization."""
        if not redis.redis_client:
            return
        
        # Handle Pydantic models
        if isinstance(value, BaseModel):
            value = value.model_dump()
        elif isinstance(value, list):
            # Handle list of Pydantic models or dicts
            value = [v.model_dump() if isinstance(v, BaseModel) else v for v in value]
        
        json_value = json.dumps(value, default=str)
        await redis.redis_client.set(key, json_value, ex=ttl or self.default_ttl)

    async def delete(self, key: str):
        """Delete a value from the cache."""
        if not redis.redis_client:
            return
        
        await redis.redis_client.delete(key)

    async def list_keys(self, pattern: str = "*") -> List[str]:
        """List keys matching a pattern."""
        if not redis.redis_client:
            return []
        
        # Keys returns strings directly due to decode_responses=True
        keys = await redis.redis_client.keys(pattern)
        return keys
