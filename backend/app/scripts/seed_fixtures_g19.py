"""
Script to seed Serie A 2025-2026 Giornata 19 fixtures (Infrasettimanale)
Run with: python -m app.scripts.seed_fixtures_g19
"""

import asyncio
import logging
from datetime import datetime
from sqlalchemy import select

from app.db.engine import AsyncSessionLocal
from app.db.models import Team, Fixture, Competition, FixtureStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Giornata 19 - Serie A 2025/2026 (6-7 Gennaio 2026 - Turno Infrasettimanale)
# NOTE: Orari da confermare dalla Lega Serie A
GIORNATA_19_FIXTURES = [
    # Martedì 6 Gennaio 2026 (orari indicativi - da confermare)
    {
        "home_team": "Bologna",
        "away_team": "Atalanta",
        "match_date": datetime(2026, 1, 6, 20, 45),
        "round": "Giornata 19"
    },
    {
        "home_team": "Cremonese",
        "away_team": "Cagliari",
        "match_date": datetime(2026, 1, 6, 20, 45),
        "round": "Giornata 19"
    },
    {
        "home_team": "Lazio",
        "away_team": "Fiorentina",
        "match_date": datetime(2026, 1, 6, 20, 45),
        "round": "Giornata 19"
    },
    {
        "home_team": "Lecce",
        "away_team": "AS Roma",
        "match_date": datetime(2026, 1, 6, 20, 45),
        "round": "Giornata 19"
    },
    {
        "home_team": "AC Milan",
        "away_team": "Genoa",
        "match_date": datetime(2026, 1, 6, 20, 45),
        "round": "Giornata 19"
    },
    {
        "home_team": "Napoli",
        "away_team": "Hellas Verona",
        "match_date": datetime(2026, 1, 6, 20, 45),
        "round": "Giornata 19"
    },
    {
        "home_team": "Pisa",
        "away_team": "Como",
        "match_date": datetime(2026, 1, 6, 20, 45),
        "round": "Giornata 19"
    },
    {
        "home_team": "Sassuolo",
        "away_team": "Juventus",
        "match_date": datetime(2026, 1, 6, 20, 45),
        "round": "Giornata 19"
    },
    {
        "home_team": "Torino",
        "away_team": "Udinese",
        "match_date": datetime(2026, 1, 6, 20, 45),
        "round": "Giornata 19"
    },
    # Mercoledì 7 Gennaio 2026
    {
        "home_team": "Parma",
        "away_team": "Inter",
        "match_date": datetime(2026, 1, 7, 20, 45),
        "round": "Giornata 19"
    },
]


async def seed_fixtures_g19():
    """Seed Giornata 19 fixtures"""
    async with AsyncSessionLocal() as session:
        logger.info("Starting Giornata 19 fixtures seeding (Serie A 2025-2026)...")

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

        for fixture_data in GIORNATA_19_FIXTURES:
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
                existing_fixture.status = fixture_data.get("status", FixtureStatus.SCHEDULED)
                existing_fixture.match_date = fixture_data["match_date"]
                if "home_score" in fixture_data:
                    existing_fixture.home_score = fixture_data["home_score"]
                if "away_score" in fixture_data:
                    existing_fixture.away_score = fixture_data["away_score"]
                fixtures_updated += 1
                logger.info(
                    f"Updated: {fixture_data['home_team']} vs {fixture_data['away_team']}"
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
                    status=fixture_data.get("status", FixtureStatus.SCHEDULED),
                    home_score=fixture_data.get("home_score"),
                    away_score=fixture_data.get("away_score")
                )
                session.add(new_fixture)
                fixtures_created += 1
                logger.info(
                    f"Created: {fixture_data['home_team']} vs {fixture_data['away_team']}"
                )

        await session.commit()
        logger.info(
            f"✅ Giornata 19 fixtures seeding completed! "
            f"Created: {fixtures_created}, Updated: {fixtures_updated}"
        )
        logger.info(f"🗓️  Saved at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(seed_fixtures_g19())
