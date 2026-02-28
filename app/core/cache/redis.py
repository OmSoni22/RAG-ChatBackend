import redis.asyncio as redis
from app.core.config.settings import settings

redis_client = None

async def init_redis():
    global redis_client
    if settings.redis_enabled:
        try:
            redis_client = redis.from_url(
                settings.redis_url, 
                encoding="utf-8", 
                decode_responses=True
            )
            # Verify connection
            await redis_client.ping()
            print("✅ Redis connection established successfully.")
        except Exception as e:
            print(f"❌ Failed to connect to Redis: {e}")
            raise e
