"""
Health Check Endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as redis
from datetime import datetime

from app.db.engine import get_db
from app.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("")
async def health_check():
    """
    Basic health check endpoint.
    Returns 200 if service is running.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "seriea-predictions-api",
        "version": "1.0.0"
    }


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness check - verifies all dependencies are ready.
    Checks database and Redis connectivity.
    """
    checks = {
        "database": "unknown",
        "redis": "unknown"
    }

    # Check database
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"

    # Check Redis
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        await redis_client.close()
        checks["redis"] = "healthy"
    except Exception as e:
        checks["redis"] = f"unhealthy: {str(e)}"

    # Overall status
    all_healthy = all(status == "healthy" for status in checks.values())

    return {
        "status": "ready" if all_healthy else "not_ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks
    }


@router.get("/live")
async def liveness_check():
    """
    Liveness check - simple endpoint to verify process is alive.
    Used by container orchestrators (Kubernetes, etc.)
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }
