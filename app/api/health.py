"""
Enhanced health check endpoints with connectivity checks and version info.
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any
import rich
from sqlalchemy import text

from app.core.db.session import AsyncSessionLocal
from app.core.config.settings import settings

router = APIRouter()


class HealthStatus(BaseModel):
    """Health check response model."""
    status: str
    version: str
    environment: str
    details: Dict[str, Any]


class ReadinessStatus(BaseModel):
    """Readiness check response model."""
    ready: bool
    checks: Dict[str, bool]


async def check_database() -> bool:
    """Check database connectivity."""
    try:
        async with AsyncSessionLocal() as session:
            # Simple query to test connection
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        rich.print("Database connection failed", e)
        return False




@router.get("/health", response_model=HealthStatus)
async def health_check():
    """
    Basic health check endpoint.
    Returns 200 if application is running.
    """
    return HealthStatus(
        status="healthy",
        version="1.0.0",
        environment="development" if settings.debug else "production",
        details={
            "app_name": settings.app_name,
        }
    )


@router.get("/health/liveness")
async def liveness_check():
    """
    Liveness probe for Kubernetes/Docker.
    Returns 200 if application process is alive.
    """
    return {"status": "alive"}


@router.get("/health/readiness", response_model=ReadinessStatus)
async def readiness_check():
    """
    Readiness probe for Kubernetes/Docker.
    Returns 200 if application is ready to serve traffic.
    Checks database connectivity.
    """
    db_healthy = await check_database()

    response = ReadinessStatus(
        ready=db_healthy,
        checks={"database": db_healthy}
    )

    if not db_healthy:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=response.model_dump()
        )

    return response
