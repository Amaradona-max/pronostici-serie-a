"""
FastAPI Main Application
Serie A Predictions Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.config import get_settings
from app.db.engine import init_db, close_db
from app.api.endpoints import fixtures, predictions, health, admin, standings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    Startup and shutdown logic
    """
    # Startup
    logger.info("Starting Serie A Predictions API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Initialize database (create tables if they don't exist)
    # This is safe because init_db uses create_all which is idempotent
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized successfully")

    logger.info("Application started successfully")

    yield

    # Shutdown
    logger.info("Shutting down...")
    await close_db()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Serie A Predictions API",
    description="ML-powered predictions for Serie A football matches",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(
    health.router,
    prefix="/api/v1/health",
    tags=["Health"]
)

app.include_router(
    fixtures.router,
    prefix="/api/v1/fixtures",
    tags=["Fixtures"]
)

app.include_router(
    predictions.router,
    prefix="/api/v1/predictions",
    tags=["Predictions"]
)

app.include_router(
    admin.router,
    prefix="/api/v1/admin",
    tags=["Admin"]
)

app.include_router(
    standings.router,
    prefix="/api/v1/standings",
    tags=["Standings & Statistics"]
)


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Serie A Predictions API",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": "server_error"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
