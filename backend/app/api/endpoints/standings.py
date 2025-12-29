"""
Standings and Statistics Endpoints
Classifica, Marcatori, Cartellini
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from app.db.engine import get_db
from app.db import models
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


# Response Models
class TeamStandingResponse(BaseModel):
    position: int
    team_name: str
    team_short_name: str
    matches_played: int
    wins: int
    draws: int
    losses: int
    goals_scored: int
    goals_conceded: int
    goal_difference: int
    points: int
    form: Optional[str] = None  # Last 5 matches: W W D L W

    class Config:
        from_attributes = True


class TopScorerResponse(BaseModel):
    position: int
    player_name: str
    team_name: str
    team_short_name: str
    goals: int
    assists: Optional[int] = 0
    matches: Optional[int] = 0


class PlayerCardResponse(BaseModel):
    player_name: str
    team_name: str
    team_short_name: str
    yellow_cards: int
    red_cards: int
    total_cards: int
    is_suspended: bool = False


class TeamCardsResponse(BaseModel):
    team_name: str
    team_short_name: str
    yellow_cards: int
    red_cards: int
    total_cards: int
    players: List[PlayerCardResponse]


@router.get("/serie-a/{season}", response_model=List[TeamStandingResponse])
async def get_standings(
    season: str = "2025-2026",
    db: AsyncSession = Depends(get_db)
):
    """
    Get Serie A standings (classifica) for the season.
    Calculated from match results.
    """
    try:
        logger.info(f"Fetching standings for season {season}")

        # Get all teams
        teams_query = select(models.Team).order_by(models.Team.name)
        teams_result = await db.execute(teams_query)
        teams = teams_result.scalars().all()

        standings = []

        for team in teams:
            # Get home matches
            home_query = select(models.Fixture).where(
                models.Fixture.home_team_id == team.id,
                models.Fixture.season == season,
                models.Fixture.status == models.FixtureStatus.FINISHED
            )
            home_fixtures = (await db.execute(home_query)).scalars().all()

            # Get away matches
            away_query = select(models.Fixture).where(
                models.Fixture.away_team_id == team.id,
                models.Fixture.season == season,
                models.Fixture.status == models.FixtureStatus.FINISHED
            )
            away_fixtures = (await db.execute(away_query)).scalars().all()

            # Calculate stats
            wins = 0
            draws = 0
            losses = 0
            goals_scored = 0
            goals_conceded = 0

            # Home matches
            for match in home_fixtures:
                goals_scored += match.home_score or 0
                goals_conceded += match.away_score or 0
                if match.home_score > match.away_score:
                    wins += 1
                elif match.home_score == match.away_score:
                    draws += 1
                else:
                    losses += 1

            # Away matches
            for match in away_fixtures:
                goals_scored += match.away_score or 0
                goals_conceded += match.home_score or 0
                if match.away_score > match.home_score:
                    wins += 1
                elif match.away_score == match.home_score:
                    draws += 1
                else:
                    losses += 1

            matches_played = len(home_fixtures) + len(away_fixtures)
            points = (wins * 3) + draws
            goal_difference = goals_scored - goals_conceded

            standings.append(TeamStandingResponse(
                position=0,  # Will be set after sorting
                team_name=team.name,
                team_short_name=team.short_name or team.code or team.name[:3].upper(),
                matches_played=matches_played,
                wins=wins,
                draws=draws,
                losses=losses,
                goals_scored=goals_scored,
                goals_conceded=goals_conceded,
                goal_difference=goal_difference,
                points=points
            ))

        # Sort by points, then goal difference, then goals scored
        standings.sort(
            key=lambda x: (-x.points, -x.goal_difference, -x.goals_scored)
        )

        # Set positions
        for i, standing in enumerate(standings, 1):
            standing.position = i

        logger.info(f"Calculated standings for {len(standings)} teams")
        return standings

    except Exception as e:
        logger.error(f"Error fetching standings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-scorers/{season}", response_model=List[TopScorerResponse])
async def get_top_scorers(
    season: str = "2025-2026",
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get top scorers (capocannonieri) for the season.
    Mock data for now - will be real when player stats are tracked.
    """
    try:
        logger.info(f"Fetching top scorers for season {season}")

        # Get some real teams for realistic data
        teams_query = select(models.Team).limit(10)
        teams_result = await db.execute(teams_query)
        teams = list(teams_result.scalars().all())

        if not teams:
            return []

        # Mock data based on real Serie A 2024/25 top scorers
        mock_scorers = [
            {"name": "Marcus Thuram", "team_idx": 0, "goals": 12, "assists": 4},
            {"name": "Mateo Retegui", "team_idx": 1, "goals": 11, "assists": 2},
            {"name": "Moise Kean", "team_idx": 2, "goals": 10, "assists": 3},
            {"name": "Romelu Lukaku", "team_idx": 3, "goals": 9, "assists": 5},
            {"name": "Lautaro Martinez", "team_idx": 0, "goals": 9, "assists": 3},
            {"name": "Ademola Lookman", "team_idx": 1, "goals": 8, "assists": 4},
            {"name": "Dusan Vlahovic", "team_idx": 4, "goals": 8, "assists": 1},
            {"name": "Artem Dovbyk", "team_idx": 5, "goals": 7, "assists": 2},
            {"name": "Christian Pulisic", "team_idx": 6, "goals": 7, "assists": 6},
            {"name": "Patrick Cutrone", "team_idx": 7, "goals": 6, "assists": 3},
        ]

        scorers = []
        for i, scorer in enumerate(mock_scorers[:limit], 1):
            team = teams[scorer["team_idx"] % len(teams)]
            scorers.append(TopScorerResponse(
                position=i,
                player_name=scorer["name"],
                team_name=team.name,
                team_short_name=team.short_name or team.code or team.name[:3].upper(),
                goals=scorer["goals"],
                assists=scorer["assists"],
                matches=15
            ))

        logger.info(f"Returning {len(scorers)} top scorers")
        return scorers

    except Exception as e:
        logger.error(f"Error fetching top scorers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cards/{season}", response_model=List[TeamCardsResponse])
async def get_cards_situation(
    season: str = "2025-2026",
    db: AsyncSession = Depends(get_db)
):
    """
    Get cards situation (yellow/red cards) for all teams.
    Shows which players are at risk of suspension.
    """
    try:
        logger.info(f"Fetching cards situation for season {season}")

        # Get all teams
        teams_query = select(models.Team).order_by(models.Team.name)
        teams_result = await db.execute(teams_query)
        teams = teams_result.scalars().all()

        teams_cards = []

        # Mock data for each team
        mock_players_per_team = [
            {"name": "N. Barella", "yellow": 4, "red": 0},
            {"name": "H. Calhanoglu", "yellow": 3, "red": 0},
            {"name": "F. Acerbi", "yellow": 5, "red": 1},
            {"name": "D. Frattesi", "yellow": 2, "red": 0},
        ]

        for team in teams:
            team_yellow = 0
            team_red = 0
            players = []

            for i, mock in enumerate(mock_players_per_team):
                # Vary the data per team
                yellow = mock["yellow"] + (hash(team.name + str(i)) % 3)
                red = mock["red"]
                is_suspended = yellow >= 4 or red >= 1

                players.append(PlayerCardResponse(
                    player_name=mock["name"],
                    team_name=team.name,
                    team_short_name=team.short_name or team.code or team.name[:3].upper(),
                    yellow_cards=yellow,
                    red_cards=red,
                    total_cards=yellow + red,
                    is_suspended=is_suspended
                ))

                team_yellow += yellow
                team_red += red

            teams_cards.append(TeamCardsResponse(
                team_name=team.name,
                team_short_name=team.short_name or team.code or team.name[:3].upper(),
                yellow_cards=team_yellow,
                red_cards=team_red,
                total_cards=team_yellow + team_red,
                players=players
            ))

        logger.info(f"Calculated cards for {len(teams_cards)} teams")
        return teams_cards

    except Exception as e:
        logger.error(f"Error fetching cards: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
