from app.core.db.session import init_db, close_db


async def bootstrap():
    """
    Initialize application services on startup.

    Note: Database migrations are handled by Alembic.
    Run 'alembic upgrade head' to apply migrations.
    """
    # Initialize DB first so failures prevent app from starting
    await init_db()


async def shutdown():
    """Shutdown/cleanup for all centralized services.

    Disposes database engine/pools.
    Safe to call multiple times.
    """
    try:
        close_db()
    except Exception as e:
        print(f"⚠️ Error disposing DB engine: {e}")
