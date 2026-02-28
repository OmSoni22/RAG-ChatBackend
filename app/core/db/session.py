from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
from app.core.config.settings import settings

engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
	"""Verify DB connectivity and ensure the connection pool is usable.

	Raises the underlying exception if a connection cannot be established.
	"""
	try:
		async with engine.connect() as conn:
			await conn.execute(text("SELECT 1"))
		print("✅ Database connection established successfully.")
	except Exception as e:
		print(f"❌ Failed to connect to Database: {e}")
		raise


def close_db():
	"""Dispose the underlying (sync) engine to close pool connections."""
	try:
		# For AsyncEngine, dispose the underlying sync engine to ensure pools are closed.
		sync_engine = getattr(engine, "sync_engine", None)
		if sync_engine is not None:
			sync_engine.dispose()
		else:
			# Fallback: attempt to call dispose on the engine itself
			engine.dispose()
		print("✅ Database engine disposed.")
	except Exception as e:
		print(f"⚠️ Error disposing DB engine: {e}")
