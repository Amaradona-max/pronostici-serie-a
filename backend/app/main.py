"""
FastAPI Main Application
Serie A Predictions Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from sqlalchemy import select, text

from app.config import get_settings
from app.db.engine import init_db, close_db, AsyncSessionLocal
from app.api.endpoints import fixtures, predictions, health, admin, standings, teams
from app.db import models

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

    # AUTO-SEEDING CHECK FOR VERCEL
    # If we are in production and the DB is empty (no teams/standings), seed them.
    if settings.is_production:
        try:
            async with AsyncSessionLocal() as session:
                # Check for teams
                result = await session.execute(select(models.Team).limit(1))
                team = result.scalar_one_or_none()
                
                if not team:
                    logger.warning("PRODUCTION: Database is empty! Starting auto-seeding...")
                    
                    # Import seed functions inside the check to avoid circular imports
                    from app.scripts.seed_teams import seed_teams
                    from app.scripts.seed_players import seed_players
                    from app.scripts.seed_standings_g17 import seed_standings
                    from app.scripts.seed_fixtures_g18 import seed_fixtures
                    
                    # 1. Seed Teams
                    logger.info("Auto-seeding Teams...")
                    await seed_teams()
                    
                    # 2. Seed Players (includes creating players)
                    logger.info("Auto-seeding Players...")
                    await seed_players()
                    
                    # 3. Seed Standings
                    logger.info("Auto-seeding Standings...")
                    await seed_standings()

                    # 4. Seed Fixtures
                    logger.info("Auto-seeding Fixtures...")
                    await seed_fixtures()
                    
                    logger.info("Auto-seeding COMPLETE.")
                else:
                    # Check for standings specifically
                    stats_result = await session.execute(
                        select(models.TeamStats).where(models.TeamStats.season == "2025-2026").limit(1)
                    )
                    stats = stats_result.scalar_one_or_none()
                    
                    if not stats:
                        logger.warning("PRODUCTION: Standings missing! Seeding standings...")
                        from app.scripts.seed_standings_g17 import seed_standings
                        await seed_standings()
                        logger.info("Standings seeded.")

        except Exception as e:
            logger.error(f"Error during auto-seeding check: {e}")

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

app.include_router(
    teams.router,
    prefix="/api/v1/teams",
    tags=["Teams"]
)
