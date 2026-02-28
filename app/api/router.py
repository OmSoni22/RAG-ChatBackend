"""
Central API router that aggregates all route modules.
"""

from fastapi import APIRouter, Depends, Query
from datetime import datetime
from typing import Optional

from app.modules.user.user_routes import router as user_router
from app.core.logging import log_reader
from app.core.logging.schemas import LogResponse

api_router = APIRouter()

# Include module routers
api_router.include_router(user_router, prefix="/users", tags=["Users"])

from app.api.cache_routes import router as cache_router
api_router.include_router(cache_router, prefix="/cache", tags=["Cache"])


# System/Logging endpoints
@api_router.get("/logs", response_model=LogResponse, tags=["System"])
async def get_logs(
    level: str = Query(..., description="Log level: debug, info, or error"),
    start_date: Optional[datetime] = Query(None, description="Filter logs after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter logs before this date"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Items per page")
):
    """
    Query application logs with filtering and pagination.
    
    - **level**: Log level to query (debug, info, error)
    - **start_date**: Optional start date filter (ISO format)
    - **end_date**: Optional end date filter (ISO format)
    - **page**: Page number (default: 1)
    - **size**: Items per page (default: 50, max: 100)
    """
    return log_reader.read_logs(level, start_date, end_date, page, size)


@api_router.get("/logs/stats", tags=["System"])
async def get_log_stats():
    """
    Get statistics about log files.
    
    Returns information about current and rotated log files for each level.
    """
    return log_reader.get_log_stats()
