from app.core.cache.redis import init_redis, redis_client
from app.core.db.session import init_db, close_db


async def bootstrap():
    """
    Initialize application services on startup.

    Note: Database migrations are handled by Alembic.
    Run 'alembic upgrade head' to apply migrations.
    """
    # Initialize DB first so failures prevent app from starting
    await init_db()

    # Then initialize Redis (optional service)
    await init_redis()


async def shutdown():
    """Shutdown/cleanup for all centralized services.

    Closes Redis (if initialized) and disposes database engine/pools.
    Safe to call multiple times.
    """
    # Close Redis if available
    try:
        if redis_client:
            await redis_client.close()
            print("✅ Redis connection closed.")
    except Exception as e:
        print(f"⚠️ Error closing Redis: {e}")

    # Dispose DB engine/pools
    try:
        close_db()
    except Exception as e:
        print(f"⚠️ Error disposing DB engine: {e}")
