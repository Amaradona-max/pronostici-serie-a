"""
Script to seed Serie A 2025-2026 Giornata 17 fixtures and results
STAGIONE CORRETTA: 2025/2026
Run with: python -m app.scripts.seed_fixtures_g17_CORRECT
"""

import asyncio
import logging
from datetime import datetime
from sqlalchemy import select

from app.db.engine import AsyncSessionLocal
from app.db.models import Team, Fixture, Competition, FixtureStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Giornata 17 - Serie A 2025/2026 (27-29 Dicembre 2025)
GIORNATA_17_FIXTURES = [
    # Sabato 27 Dicembre 2025
    {
        "home_team": "Parma",
        "away_team": "Fiorentina",
        "home_score": 1,
        "away_score": 0,
        "match_date": datetime(2025, 12, 27, 12, 30),
        "round": "Giornata 17"
    },
    {
        "home_team": "Lecce",
        "away_team": "Como",
        "home_score": 0,
        "away_score": 3,
        "match_date": datetime(2025, 12, 27, 15, 0),
        "round": "Giornata 17"
    },
    {
        "home_team": "Torino",
        "away_team": "Cagliari",
        "home_score": 1,
        "away_score": 2,
        "match_date": datetime(2025, 12, 27, 15, 0),
        "round": "Giornata 17"
    },
    {
        "home_team": "Udinese",
        "away_team": "Lazio",
        "home_score": 1,
        "away_score": 1,
        "match_date": datetime(2025, 12, 27, 18, 0),
        "round": "Giornata 17"
    },
    {
        "home_team": "Pisa",
        "away_team": "Juventus",
        "home_score": 0,
        "away_score": 2,
        "match_date": datetime(2025, 12, 27, 20, 45),
        "round": "Giornata 17"
    },
    # Domenica 28 Dicembre 2025
    {
        "home_team": "AC Milan",
        "away_team": "Hellas Verona",
        "home_score": 3,
        "away_score": 0,
        "match_date": datetime(2025, 12, 28, 12, 30),
        "round": "Giornata 17"
    },
    {
        "home_team": "Cremonese",
        "away_team": "Napoli",
        "home_score": 0,
        "away_score": 2,
        "match_date": datetime(2025, 12, 28, 15, 0),
        "round": "Giornata 17"
    },
    {
        "home_team": "Bologna",
        "away_team": "Sassuolo",
        "home_score": 1,
        "away_score": 1,
        "match_date": datetime(2025, 12, 28, 18, 0),
        "round": "Giornata 17"
    },
    {
        "home_team": "Atalanta",
        "away_team": "Inter",
        "home_score": 0,
        "away_score": 1,
        "match_date": datetime(2025, 12, 28, 20, 45),
        "round": "Giornata 17"
    },
    # Lunedì 29 Dicembre 2025
    {
        "home_team": "AS Roma",
        "away_team": "Genoa",
        "home_score": 3,
        "away_score": 1,
        "match_date": datetime(2025, 12, 29, 20, 45),
        "round": "Giornata 17"
    },
]


async def seed_fixtures_g17():
    """Seed Giornata 17 fixtures with results"""
    async with AsyncSessionLocal() as session:
        logger.info("Starting Giornata 17 fixtures seeding (Serie A 2025-2026)...")

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
        logger.info(f"🗓️  Saved at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(seed_fixtures_g17())
