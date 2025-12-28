"""
Fixtures API Endpoints
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional
from datetime import date, datetime

from app.db.engine import get_db
from app.db.models import Fixture, Team, Stadium, Prediction, TeamStats, Injury, Suspension
from app.api.schemas import (
    FixtureListResponse,
    FixtureBase,
    MatchDetailResponse,
    PredictionResponse,
    TeamStatsResponse,
    InjuryResponse,
    SuspensionResponse,
    TeamBase,
    StadiumInfo
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/serie-a/{season}",
    response_model=FixtureListResponse,
    summary="List Serie A fixtures"
)
async def get_fixtures(
    season: str = "2025-2026",
    round: Optional[str] = Query(None),
    team_id: Optional[int] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    status: str = Query("scheduled"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of Serie A fixtures with optional filters.

    Args:
        season: Season (e.g., "2025-2026")
        round: Filter by round (e.g., "Giornata 15")
        team_id: Filter by team
        date_from: Filter by date range start
        date_to: Filter by date range end
        status: Filter by status (scheduled, live, finished)
        page: Page number
        page_size: Results per page

    Returns:
        Paginated list of fixtures
    """
    try:
        # Build query
        query = select(Fixture).where(Fixture.season == season)

        if round:
            query = query.where(Fixture.round == round)

        if team_id:
            query = query.where(
                or_(
                    Fixture.home_team_id == team_id,
                    Fixture.away_team_id == team_id
                )
            )

        if date_from:
            query = query.where(Fixture.match_date >= datetime.combine(date_from, datetime.min.time()))

        if date_to:
            query = query.where(Fixture.match_date <= datetime.combine(date_to, datetime.max.time()))

        if status:
            query = query.where(Fixture.status == status)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar()

        # Add pagination and eager loading
        query = query.options(
            selectinload(Fixture.home_team),
            selectinload(Fixture.away_team),
            selectinload(Fixture.stadium)
        ).order_by(Fixture.match_date).offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        fixtures = result.scalars().all()

        # Convert to response models
        fixture_responses = []
        for f in fixtures:
            fixture_responses.append(FixtureBase(
                id=f.id,
                home_team=TeamBase.model_validate(f.home_team),
                away_team=TeamBase.model_validate(f.away_team),
                match_date=f.match_date,
                round=f.round,
                status=f.status,
                stadium=StadiumInfo.model_validate(f.stadium) if f.stadium else None,
                home_score=f.home_score,
                away_score=f.away_score
            ))

        return FixtureListResponse(
            fixtures=fixture_responses,
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        logger.error(f"Error fetching fixtures: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{fixture_id}",
    response_model=MatchDetailResponse,
    summary="Get match detail with prediction"
)
async def get_match_detail(
    fixture_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information for a single match including:
    - Fixture details
    - Prediction probabilities
    - Team statistics
    - Injuries and suspensions
    - Recent form
    - Head-to-head history
    """
    try:
        # Get fixture with relationships
        query = select(Fixture).where(Fixture.id == fixture_id).options(
            selectinload(Fixture.home_team),
            selectinload(Fixture.away_team),
            selectinload(Fixture.stadium),
            selectinload(Fixture.predictions)
        )

        result = await db.execute(query)
        fixture = result.scalar_one_or_none()

        if not fixture:
            raise HTTPException(status_code=404, detail="Fixture not found")

        # Get latest prediction
        prediction = None
        if fixture.predictions:
            latest_pred = max(fixture.predictions, key=lambda p: p.computed_at)
            prediction = PredictionResponse.model_validate(latest_pred)

        # Get team stats
        home_stats_query = select(TeamStats).where(
            and_(
                TeamStats.team_id == fixture.home_team_id,
                TeamStats.season == fixture.season
            )
        )
        home_stats = (await db.execute(home_stats_query)).scalar_one_or_none()

        away_stats_query = select(TeamStats).where(
            and_(
                TeamStats.team_id == fixture.away_team_id,
                TeamStats.season == fixture.season
            )
        )
        away_stats = (await db.execute(away_stats_query)).scalar_one_or_none()

        # Get injuries
        home_injuries_query = select(Injury).join(Injury.player).where(
            and_(
                Injury.team_id == fixture.home_team_id,
                Injury.status == 'active'
            )
        )
        home_injuries_result = await db.execute(home_injuries_query)
        home_injuries = home_injuries_result.scalars().all()

        away_injuries_query = select(Injury).join(Injury.player).where(
            and_(
                Injury.team_id == fixture.away_team_id,
                Injury.status == 'active'
            )
        )
        away_injuries_result = await db.execute(away_injuries_query)
        away_injuries = away_injuries_result.scalars().all()

        # Get suspensions
        home_suspensions_query = select(Suspension).join(Suspension.player).where(
            and_(
                Suspension.team_id == fixture.home_team_id,
                Suspension.status == 'active'
            )
        )
        home_suspensions_result = await db.execute(home_suspensions_query)
        home_suspensions = home_suspensions_result.scalars().all()

        away_suspensions_query = select(Suspension).join(Suspension.player).where(
            and_(
                Suspension.team_id == fixture.away_team_id,
                Suspension.status == 'active'
            )
        )
        away_suspensions_result = await db.execute(away_suspensions_query)
        away_suspensions = away_suspensions_result.scalars().all()

        # Build response
        return MatchDetailResponse(
            fixture=FixtureBase.model_validate(fixture),
            prediction=prediction,
            home_team_stats=TeamStatsResponse.model_validate(home_stats) if home_stats else None,
            away_team_stats=TeamStatsResponse.model_validate(away_stats) if away_stats else None,
            home_injuries=[
                InjuryResponse(
                    player_name=inj.player.name,
                    injury_type=inj.injury_type or "Unknown",
                    severity=inj.severity,
                    expected_return=inj.expected_return_date
                )
                for inj in home_injuries
            ],
            away_injuries=[
                InjuryResponse(
                    player_name=inj.player.name,
                    injury_type=inj.injury_type or "Unknown",
                    severity=inj.severity,
                    expected_return=inj.expected_return_date
                )
                for inj in away_injuries
            ],
            home_suspensions=[
                SuspensionResponse(
                    player_name=susp.player.name,
                    reason=susp.reason,
                    matches_remaining=susp.matches_remaining
                )
                for susp in home_suspensions
            ],
            away_suspensions=[
                SuspensionResponse(
                    player_name=susp.player.name,
                    reason=susp.reason,
                    matches_remaining=susp.matches_remaining
                )
                for susp in away_suspensions
            ],
            home_last_5_results=[],  # TODO: Calculate from fixtures
            away_last_5_results=[],  # TODO: Calculate from fixtures
            h2h_summary=None  # TODO: Calculate H2H stats
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching match detail: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
