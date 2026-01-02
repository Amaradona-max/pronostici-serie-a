"""
Health Check Endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as redis
from datetime import datetime
import os
import logging

from app.db.engine import get_db
from app.config import get_settings

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)


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
    Includes Debug Info for Vercel.
    """
    checks = {
        "database": "unknown",
        "redis": "unknown"
    }

    # Debug DB file
    db_path_info = "unknown"
    try:
        db_url = settings.DATABASE_URL
        checks["db_url_masked"] = db_url.split("://")[0] + "://..." 
        
        if "sqlite" in db_url:
            # Extract path from URL (sqlite+aiosqlite:///path)
            # Handle absolute paths (////) vs relative (///)
            if "////" in db_url:
                path = db_url.split(":////")[1]
                path = "/" + path # Restore leading slash for absolute path
            else:
                path = db_url.split(":///")[1]
            
            checks["db_path_resolved"] = path
            
            if os.path.exists(path):
                size = os.path.getsize(path)
                db_path_info = f"Exists. Size: {size} bytes."
                
                # Check tables count
                result = await db.execute(text("SELECT count(*) FROM sqlite_master WHERE type='table'"))
                table_count = result.scalar()
                db_path_info += f" Tables: {table_count}."
                
                # Check TeamStats specifically
                try:
                    result = await db.execute(text("SELECT count(*) FROM team_stats WHERE season='2025-2026'"))
                    stats_count = result.scalar()
                    db_path_info += f" TeamStats 25/26: {stats_count}."
                except Exception as e:
                     db_path_info += f" TeamStats check failed: {str(e)}."

            else:
                db_path_info = f"MISSING at {path}. CWD: {os.getcwd()}."
                try:
                    files = os.listdir(os.getcwd())
                    db_path_info += f" Files in CWD: {files[:10]}..." # Limit output
                except:
                    pass
                
                # Try to list 'api' directory if relative
                try:
                    if os.path.exists("api"):
                         db_path_info += f" Files in api/: {os.listdir('api')}"
                except:
                    pass
    except Exception as e:
        db_path_info = f"Error checking DB file: {str(e)}"
    
    checks["db_file_debug"] = db_path_info

    # Check database connection
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"

    # Check Redis (Optional)
    try:
        # redis_client = redis.from_url(settings.REDIS_URL)
        # await redis_client.ping()
        # await redis_client.close()
        checks["redis"] = "skipped" # Skip redis for Vercel
    except Exception as e:
        checks["redis"] = f"unhealthy: {str(e)}"

    # Overall status
    # Database must be healthy
    is_ready = checks["database"] == "healthy"

    return {
        "status": "ready" if is_ready else "not_ready",
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
