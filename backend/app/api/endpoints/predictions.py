"""
Predictions API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.engine import get_db
from app.db.models import Prediction, Fixture
from app.api.schemas import PredictionResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/{fixture_id}",
    response_model=PredictionResponse,
    summary="Get prediction for a fixture"
)
async def get_prediction(
    fixture_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get latest prediction for a fixture"""
    try:
        query = select(Prediction).where(
            Prediction.fixture_id == fixture_id
        ).order_by(Prediction.computed_at.desc()).limit(1)

        result = await db.execute(query)
        prediction = result.scalar_one_or_none()

        if not prediction:
            raise HTTPException(
                status_code=404,
                detail=f"No prediction found for fixture {fixture_id}"
            )

        return PredictionResponse.model_validate(prediction)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/history/{fixture_id}",
    response_model=List[PredictionResponse],
    summary="Get prediction history for a fixture"
)
async def get_prediction_history(
    fixture_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all prediction versions for a fixture.
    Useful for seeing how predictions changed over time (T-48h, T-24h, T-1h, etc.)
    """
    try:
        query = select(Prediction).where(
            Prediction.fixture_id == fixture_id
        ).order_by(Prediction.computed_at.desc())

        result = await db.execute(query)
        predictions = result.scalars().all()

        if not predictions:
            raise HTTPException(
                status_code=404,
                detail=f"No predictions found for fixture {fixture_id}"
            )

        return [PredictionResponse.model_validate(p) for p in predictions]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching prediction history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/recompute/{fixture_id}",
    response_model=PredictionResponse,
    summary="[ADMIN] Force recompute prediction"
)
async def recompute_prediction(
    fixture_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Force recompute prediction for a fixture.
    Useful for manual updates or debugging.

    NOTE: In production, this should be protected with admin authentication.
    """
    try:
        # Check fixture exists
        query = select(Fixture).where(Fixture.id == fixture_id)
        result = await db.execute(query)
        fixture = result.scalar_one_or_none()

        if not fixture:
            raise HTTPException(status_code=404, detail="Fixture not found")

        # TODO: Trigger prediction computation task
        # For now, return placeholder
        raise HTTPException(
            status_code=501,
            detail="Recompute endpoint not yet implemented. Use Celery task directly."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recomputing prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
