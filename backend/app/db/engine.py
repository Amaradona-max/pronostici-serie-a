"""
Database Engine and Session Management
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    pool_pre_ping=True,
    poolclass=NullPool if settings.is_production else None,
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncSession:
    """
    Dependency for getting database session in FastAPI endpoints.

    Usage:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """
    Initialize database - create all tables.

    WARNING: In production, use Alembic migrations instead.
    """
    from app.db.base import Base

    async with engine.begin() as conn:
        # For development only - creates all tables
        # In production, use Alembic migrations
        if not settings.is_production:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created")


async def close_db():
    """Close database connections"""
    await engine.dispose()
    logger.info("Database connections closed")
