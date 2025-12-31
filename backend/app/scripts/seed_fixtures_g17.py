"""
Script to seed Serie A 2025-2026 Giornata 17 fixtures and results
Run with: python -m app.scripts.seed_fixtures_g17
"""

import asyncio
import logging
from datetime import datetime
from sqlalchemy import select

from app.db.engine import AsyncSessionLocal
from app.db.models import Team, Fixture, Competition, FixtureStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Giornata 17 - Serie A 2025/2026 (20-23 Dicembre 2024)
GIORNATA_17_FIXTURES = [
    # Venerdì 20 Dicembre
    {
        "home_team": "Hellas Verona",
        "away_team": "AC Milan",
        "home_score": 0,
        "away_score": 1,
        "match_date": datetime(2024, 12, 20, 20, 45),
        "round": "Giornata 17"
    },
    # Sabato 21 Dicembre
    {
        "home_team": "Torino",
        "away_team": "Bologna",
        "home_score": 0,
        "away_score": 2,
        "match_date": datetime(2024, 12, 21, 15, 0),
        "round": "Giornata 17"
    },
    {
        "home_team": "Genoa",
        "away_team": "Napoli",
        "home_score": 1,
        "away_score": 2,
        "match_date": datetime(2024, 12, 21, 18, 0),
        "round": "Giornata 17"
    },
    {
        "home_team": "Lecce",
        "away_team": "Lazio",
        "home_score": 1,
        "away_score": 2,
        "match_date": datetime(2024, 12, 21, 20, 45),
        "round": "Giornata 17"
    },
    # Domenica 22 Dicembre
    {
        "home_team": "AS Roma",
        "away_team": "Parma",
        "home_score": 5,
        "away_score": 0,
        "match_date": datetime(2024, 12, 22, 12, 30),
        "round": "Giornata 17"
    },
    {
        "home_team": "Venezia",
        "away_team": "Cagliari",
        "home_score": 2,
        "away_score": 1,
        "match_date": datetime(2024, 12, 22, 15, 0),
        "round": "Giornata 17"
    },
    {
        "home_team": "Atalanta",
        "away_team": "Empoli",
        "home_score": 3,
        "away_score": 2,
        "match_date": datetime(2024, 12, 22, 18, 0),
        "round": "Giornata 17"
    },
    {
        "home_team": "Monza",
        "away_team": "Juventus",
        "home_score": 1,
        "away_score": 2,
        "match_date": datetime(2024, 12, 22, 20, 45),
        "round": "Giornata 17"
    },
    # Lunedì 23 Dicembre
    {
        "home_team": "Fiorentina",
        "away_team": "Udinese",
        "home_score": 1,
        "away_score": 2,
        "match_date": datetime(2024, 12, 23, 18, 30),
        "round": "Giornata 17"
    },
    {
        "home_team": "Inter",
        "away_team": "Como",
        "home_score": 2,
        "away_score": 0,
        "match_date": datetime(2024, 12, 23, 20, 45),
        "round": "Giornata 17"
    },
]


async def seed_fixtures_g17():
    """Seed Giornata 17 fixtures with results"""
    async with AsyncSessionLocal() as session:
        logger.info("Starting Giornata 17 fixtures seeding...")

        # Get or create competition
        comp_stmt = select(Competition).where(
            Competition.name == "Serie A",
            Competition.season == "2025-2026"
        )
        competition = (await session.execute(comp_stmt)).scalar_one_or_none()

        if not competition:
            competition = Competition(
                name="Serie A",
                country="Italy",
                season="2025-2026",
                external_id=135
            )
            session.add(competition)
            await session.commit()
            await session.refresh(competition)
            logger.info("Created Serie A 2025-2026 competition")

        # Get all teams
        teams_stmt = select(Team)
        teams_result = await session.execute(teams_stmt)
        teams = {team.name: team for team in teams_result.scalars().all()}

        fixtures_created = 0
        fixtures_updated = 0

        for fixture_data in GIORNATA_17_FIXTURES:
            home_team = teams.get(fixture_data["home_team"])
            away_team = teams.get(fixture_data["away_team"])

            if not home_team or not away_team:
                logger.warning(
                    f"Teams not found for {fixture_data['home_team']} vs {fixture_data['away_team']}"
                )
                continue

            # Check if fixture already exists
            fixture_stmt = select(Fixture).where(
                Fixture.home_team_id == home_team.id,
                Fixture.away_team_id == away_team.id,
                Fixture.round == fixture_data["round"]
            )
            existing_fixture = (await session.execute(fixture_stmt)).scalar_one_or_none()

            if existing_fixture:
                # Update existing fixture
                existing_fixture.home_score = fixture_data["home_score"]
                existing_fixture.away_score = fixture_data["away_score"]
                existing_fixture.status = FixtureStatus.FINISHED
                existing_fixture.match_date = fixture_data["match_date"]
                fixtures_updated += 1
                logger.info(
                    f"Updated: {fixture_data['home_team']} {fixture_data['home_score']}-"
                    f"{fixture_data['away_score']} {fixture_data['away_team']}"
                )
            else:
                # Create new fixture
                new_fixture = Fixture(
                    competition_id=competition.id,
                    season="2025-2026",
                    round=fixture_data["round"],
                    match_date=fixture_data["match_date"],
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    home_score=fixture_data["home_score"],
                    away_score=fixture_data["away_score"],
                    status=FixtureStatus.FINISHED
                )
                session.add(new_fixture)
                fixtures_created += 1
                logger.info(
                    f"Created: {fixture_data['home_team']} {fixture_data['home_score']}-"
                    f"{fixture_data['away_score']} {fixture_data['away_team']}"
                )

        await session.commit()
        logger.info(
            f"✅ Giornata 17 fixtures seeding completed! "
            f"Created: {fixtures_created}, Updated: {fixtures_updated}"
        )


if __name__ == "__main__":
    asyncio.run(seed_fixtures_g17())
