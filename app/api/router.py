"""
Central API router that aggregates all route modules.
"""

from fastapi import APIRouter, Depends, Query
from datetime import datetime
from typing import Optional

from app.modules.context.context_routes import router as context_router
from app.modules.chat.chat_routes import router as chat_router
from app.core.logging import log_reader
from app.core.logging.schemas import LogResponse

api_router = APIRouter()

# ─── Feature routers ──────────────────────────────────────────────────────────
api_router.include_router(context_router, prefix="/context", tags=["Context"])
api_router.include_router(chat_router, prefix="/chat", tags=["Chat"])

# ─── Cache router ─────────────────────────────────────────────────────────────
from app.api.cache_routes import router as cache_router
api_router.include_router(cache_router, prefix="/cache", tags=["Cache"])


# ─── System / Logging endpoints ───────────────────────────────────────────────
@api_router.get("/logs", response_model=LogResponse, tags=["System"])
async def get_logs(
    level: str = Query(..., description="Log level: debug, info, or error"),
    start_date: Optional[datetime] = Query(None, description="Filter logs after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter logs before this date"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Items per page"),
):
    """
    Query application logs with filtering and pagination.
    """
    return log_reader.read_logs(level, start_date, end_date, page, size)


@api_router.get("/logs/stats", tags=["System"])
async def get_log_stats():
    """
    Get statistics about log files.
    """
    return log_reader.get_log_stats()
