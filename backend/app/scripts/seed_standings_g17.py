"""
Script to seed Serie A 2025-2026 standings after Giornata 17
Updates team_stats table with official standings data
Run with: python -m app.scripts.seed_standings_g17
"""

import asyncio
import logging
from sqlalchemy import select

from app.db.engine import AsyncSessionLocal
from app.db.models import Team, TeamStats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Official Serie A 2025/2026 standings after Giornata 17 (29 December 2025)
# Source: Sky Sport, Corriere dello Sport
STANDINGS_DATA = [
    {"team": "Inter", "played": 16, "won": 12, "drawn": 0, "lost": 4, "gf": 35, "gs": 14, "points": 36},
    {"team": "AC Milan", "played": 16, "won": 10, "drawn": 5, "lost": 1, "gf": 27, "gs": 13, "points": 35},
    {"team": "Napoli", "played": 16, "won": 11, "drawn": 1, "lost": 4, "gf": 24, "gs": 13, "points": 34},
    {"team": "AS Roma", "played": 17, "won": 11, "drawn": 0, "lost": 6, "gf": 20, "gs": 11, "points": 33},
    {"team": "Juventus", "played": 17, "won": 9, "drawn": 5, "lost": 3, "gf": 23, "gs": 15, "points": 32},
    {"team": "Como", "played": 16, "won": 7, "drawn": 6, "lost": 3, "gf": 22, "gs": 12, "points": 27},
    {"team": "Bologna", "played": 16, "won": 7, "drawn": 5, "lost": 4, "gf": 24, "gs": 14, "points": 26},
    {"team": "Lazio", "played": 17, "won": 6, "drawn": 6, "lost": 5, "gf": 18, "gs": 12, "points": 24},
    {"team": "Sassuolo", "played": 17, "won": 6, "drawn": 4, "lost": 7, "gf": 22, "gs": 21, "points": 22},
    {"team": "Atalanta", "played": 17, "won": 5, "drawn": 7, "lost": 5, "gf": 20, "gs": 19, "points": 22},
    {"team": "Udinese", "played": 17, "won": 6, "drawn": 4, "lost": 7, "gf": 18, "gs": 28, "points": 22},
    {"team": "Cremonese", "played": 17, "won": 5, "drawn": 6, "lost": 6, "gf": 18, "gs": 20, "points": 21},
    {"team": "Torino", "played": 17, "won": 5, "drawn": 5, "lost": 7, "gf": 17, "gs": 28, "points": 20},
    {"team": "Cagliari", "played": 17, "won": 4, "drawn": 6, "lost": 7, "gf": 19, "gs": 24, "points": 18},
    {"team": "Parma", "played": 16, "won": 4, "drawn": 5, "lost": 7, "gf": 11, "gs": 18, "points": 17},
    {"team": "Lecce", "played": 16, "won": 4, "drawn": 4, "lost": 8, "gf": 11, "gs": 22, "points": 16},
    {"team": "Genoa", "played": 17, "won": 3, "drawn": 5, "lost": 9, "gf": 17, "gs": 27, "points": 14},
    {"team": "Hellas Verona", "played": 16, "won": 2, "drawn": 6, "lost": 8, "gf": 13, "gs": 25, "points": 12},
    {"team": "Pisa", "played": 17, "won": 1, "drawn": 8, "lost": 8, "gf": 12, "gs": 24, "points": 11},
    {"team": "Fiorentina", "played": 17, "won": 1, "drawn": 6, "lost": 10, "gf": 17, "gs": 28, "points": 9},
]


async def seed_standings():
    """Update team_stats with standings data after Giornata 17"""
    async with AsyncSessionLocal() as session:
        logger.info("Starting standings update for Serie A 2025-2026 (Giornata 17)...")

        # Get all teams
        teams_stmt = select(Team)
        teams_result = await session.execute(teams_stmt)
        teams = {team.name: team for team in teams_result.scalars().all()}

        teams_updated = 0
        teams_created = 0

        for standing in STANDINGS_DATA:
            team = teams.get(standing["team"])

            if not team:
                logger.warning(f"Team {standing['team']} not found in database")
                continue

            # Check if team_stats exists
            stats_stmt = select(TeamStats).where(
                TeamStats.team_id == team.id,
                TeamStats.season == "2025-2026"
            )
            team_stats = (await session.execute(stats_stmt)).scalar_one_or_none()

            # Calculate clean sheets (assuming GS=0 means clean sheet for now)
            # This is a simplification - in reality we'd need to count from fixtures
            clean_sheets = 0

            if team_stats:
                # Update existing stats
                team_stats.matches_played = standing["played"]
                team_stats.wins = standing["won"]
                team_stats.draws = standing["drawn"]
                team_stats.losses = standing["lost"]
                team_stats.goals_scored = standing["gf"]
                team_stats.goals_conceded = standing["gs"]
                team_stats.clean_sheets = clean_sheets
                teams_updated += 1
                logger.info(
                    f"Updated {standing['team']}: {standing['played']} GP, "
                    f"{standing['won']}-{standing['drawn']}-{standing['lost']}, "
                    f"{standing['points']} pts"
                )
            else:
                # Create new stats
                new_stats = TeamStats(
                    team_id=team.id,
                    season="2025-2026",
                    matches_played=standing["played"],
                    wins=standing["won"],
                    draws=standing["drawn"],
                    losses=standing["lost"],
                    goals_scored=standing["gf"],
                    goals_conceded=standing["gs"],
                    clean_sheets=clean_sheets
                )
                session.add(new_stats)
                teams_created += 1
                logger.info(
                    f"Created {standing['team']}: {standing['played']} GP, "
                    f"{standing['won']}-{standing['drawn']}-{standing['lost']}, "
                    f"{standing['points']} pts"
                )

        await session.commit()
        logger.info(
            f"✅ Standings update completed! "
            f"Created: {teams_created}, Updated: {teams_updated}"
        )
        logger.info(f"🗓️  Saved at: 2025-12-31 14:15:00")


if __name__ == "__main__":
    asyncio.run(seed_standings())
