#!/usr/bin/env python3
"""
Calculate Standings from Fixtures
Computes standings directly from finished fixtures in database
"""
import asyncio
import sys
import os
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db.engine import AsyncSessionLocal
from app.db.models import Fixture, Team, TeamStats, FixtureStatus


async def calculate_standings():
    """
    Calculate standings from all finished fixtures
    """
    print("=" * 80)
    print("📊 CALCULATING STANDINGS FROM FIXTURES")
    print("=" * 80)
    print()

    season = "2025-2026"

    async with AsyncSessionLocal() as session:
        try:
            # Get all teams
            print("📋 Loading teams...")
            teams_stmt = select(Team)
            teams_result = await session.execute(teams_stmt)
            teams = {team.id: team for team in teams_result.scalars().all()}
            print(f"✅ Loaded {len(teams)} teams")
            print()

            # Get all finished fixtures
            print("📋 Loading finished fixtures...")
            fixtures_stmt = select(Fixture).where(
                and_(
                    Fixture.season == season,
                    Fixture.status == FixtureStatus.FINISHED
                )
            )
            fixtures = (await session.execute(fixtures_stmt)).scalars().all()
            print(f"✅ Found {len(fixtures)} finished matches")
            print()

            if not fixtures:
                print("⚠️  No finished fixtures found!")
                print("   Standings will be initialized with 0 points for all teams")
                print()

            # Initialize standings
            print("🔢 Calculating standings...")
            standings = {}
            for team_id, team in teams.items():
                standings[team_id] = {
                    "team_id": team_id,
                    "team_name": team.name,
                    "played": 0,
                    "won": 0,
                    "drawn": 0,
                    "lost": 0,
                    "goals_for": 0,
                    "goals_against": 0,
                    "goal_difference": 0,
                    "points": 0
                }

            # Calculate from fixtures
            for fixture in fixtures:
                if fixture.home_score is None or fixture.away_score is None:
                    continue

                home_id = fixture.home_team_id
                away_id = fixture.away_team_id
                home_score = fixture.home_score
                away_score = fixture.away_score

                # Update matches played
                standings[home_id]["played"] += 1
                standings[away_id]["played"] += 1

                # Update goals
                standings[home_id]["goals_for"] += home_score
                standings[home_id]["goals_against"] += away_score
                standings[away_id]["goals_for"] += away_score
                standings[away_id]["goals_against"] += home_score

                # Update results and points
                if home_score > away_score:
                    standings[home_id]["won"] += 1
                    standings[home_id]["points"] += 3
                    standings[away_id]["lost"] += 1
                elif home_score < away_score:
                    standings[away_id]["won"] += 1
                    standings[away_id]["points"] += 3
                    standings[home_id]["lost"] += 1
                else:
                    standings[home_id]["drawn"] += 1
                    standings[home_id]["points"] += 1
                    standings[away_id]["drawn"] += 1
                    standings[away_id]["points"] += 1

            # Calculate goal difference
            for team_id in standings:
                standings[team_id]["goal_difference"] = (
                    standings[team_id]["goals_for"] - standings[team_id]["goals_against"]
                )

            # Sort standings
            sorted_standings = sorted(
                standings.values(),
                key=lambda x: (x["points"], x["goal_difference"], x["goals_for"]),
                reverse=True
            )

            # Update database
            print("💾 Saving to database...")
            for position, team_standing in enumerate(sorted_standings, 1):
                team_id = team_standing["team_id"]

                # Find or create TeamStats
                stats_stmt = select(TeamStats).where(
                    and_(
                        TeamStats.team_id == team_id,
                        TeamStats.season == season
                    )
                )
                stats = (await session.execute(stats_stmt)).scalar_one_or_none()

                if not stats:
                    stats = TeamStats(
                        team_id=team_id,
                        season=season
                    )
                    session.add(stats)

                # Update stats
                stats.position = position
                stats.matches_played = team_standing["played"]
                stats.wins = team_standing["won"]
                stats.draws = team_standing["drawn"]
                stats.losses = team_standing["lost"]
                stats.goals_scored = team_standing["goals_for"]
                stats.goals_conceded = team_standing["goals_against"]
                stats.goal_difference = team_standing["goal_difference"]
                stats.points = team_standing["points"]

            await session.commit()
            print()

            # Display standings
            print("=" * 80)
            print("✅ STANDINGS CALCULATED!")
            print("=" * 80)
            print()
            print(f"{'Pos':<4} {'Team':<25} {'P':<4} {'W':<4} {'D':<4} {'L':<4} {'GF':<4} {'GA':<4} {'GD':<5} {'Pts':<4}")
            print("-" * 80)

            for i, team in enumerate(sorted_standings, 1):
                print(
                    f"{i:<4} {team['team_name']:<25} "
                    f"{team['played']:<4} {team['won']:<4} {team['drawn']:<4} {team['lost']:<4} "
                    f"{team['goals_for']:<4} {team['goals_against']:<4} "
                    f"{team['goal_difference']:<5} {team['points']:<4}"
                )

            print()
            return True

        except Exception as e:
            print()
            print("=" * 80)
            print(f"❌ ERROR: {e}")
            print("=" * 80)
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    print()
    success = asyncio.run(calculate_standings())

    if success:
        print("✅ Standings calculation completed!")
        print()
        sys.exit(0)
    else:
        print("❌ Standings calculation failed!")
        sys.exit(1)
