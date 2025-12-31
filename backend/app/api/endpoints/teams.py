"""
Teams API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from app.db.engine import get_db
from app.db.models import Team
from app.api.schemas import TeamBase

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[TeamBase])
async def get_teams(db: AsyncSession = Depends(get_db)):
    """
    Get all teams.

    Returns:
        List of all teams in the database
    """
    try:
        query = select(Team).order_by(Team.name)
        result = await db.execute(query)
        teams = result.scalars().all()

        return [TeamBase.model_validate(team) for team in teams]

    except Exception as e:
        logger.error(f"Error fetching teams: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{team_id}", response_model=TeamBase)
async def get_team(team_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a specific team by ID.

    Args:
        team_id: The team ID

    Returns:
        Team details
    """
    try:
        query = select(Team).where(Team.id == team_id)
        result = await db.execute(query)
        team = result.scalar_one_or_none()

        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        return TeamBase.model_validate(team)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching team {team_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
