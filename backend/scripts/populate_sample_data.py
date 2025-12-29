"""
Populate database with sample Serie A 2025-2026 data
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from datetime import datetime, timedelta
from app.db.engine import AsyncSessionLocal
from app.db import models


# Serie A teams 2025-2026
SERIE_A_TEAMS = [
    {"name": "Inter", "short_name": "INT", "code": "INT", "external_id": 505},
    {"name": "AC Milan", "short_name": "MIL", "code": "MIL", "external_id": 489},
    {"name": "Juventus", "short_name": "JUV", "code": "JUV", "external_id": 496},
    {"name": "Napoli", "short_name": "NAP", "code": "NAP", "external_id": 492},
    {"name": "AS Roma", "short_name": "ROM", "code": "ROM", "external_id": 497},
    {"name": "Lazio", "short_name": "LAZ", "code": "LAZ", "external_id": 487},
    {"name": "Atalanta", "short_name": "ATA", "code": "ATA", "external_id": 499},
    {"name": "Fiorentina", "short_name": "FIO", "code": "FIO", "external_id": 502},
    {"name": "Bologna", "short_name": "BOL", "code": "BOL", "external_id": 500},
    {"name": "Torino", "short_name": "TOR", "code": "TOR", "external_id": 503},
    {"name": "Udinese", "short_name": "UDI", "code": "UDI", "external_id": 494},
    {"name": "Monza", "short_name": "MON", "code": "MON", "external_id": 1579},
    {"name": "Genoa", "short_name": "GEN", "code": "GEN", "external_id": 495},
    {"name": "Lecce", "short_name": "LEC", "code": "LEC", "external_id": 867},
    {"name": "Hellas Verona", "short_name": "VER", "code": "VER", "external_id": 504},
    {"name": "Cagliari", "short_name": "CAG", "code": "CAG", "external_id": 490},
    {"name": "Empoli", "short_name": "EMP", "code": "EMP", "external_id": 511},
    {"name": "Parma", "short_name": "PAR", "code": "PAR", "external_id": 488},
    {"name": "Como", "short_name": "COM", "code": "COM", "external_id": 512},
    {"name": "Venezia", "short_name": "VEN", "code": "VEN", "external_id": 517},
]


async def create_competition(session):
    """Create Serie A 2025-2026 competition"""
    competition = models.Competition(
        name="Serie A",
        country="Italy",
        season="2025-2026",
        external_id=135
    )
    session.add(competition)
    await session.flush()
    return competition


async def create_teams(session):
    """Create Serie A teams"""
    teams = []
    for team_data in SERIE_A_TEAMS:
        team = models.Team(**team_data)
        session.add(team)
        teams.append(team)

    await session.flush()
    return teams


async def create_fixtures(session, competition, teams):
    """Create sample fixtures for upcoming matches"""
    fixtures = []

    # Start from next week
    base_date = datetime.now() + timedelta(days=7)

    # Create fixtures for Giornata 19 (example)
    matchups = [
        (0, 1),   # Inter vs Milan (Derby)
        (2, 3),   # Juventus vs Napoli
        (4, 5),   # Roma vs Lazio (Derby)
        (6, 7),   # Atalanta vs Fiorentina
        (8, 9),   # Bologna vs Torino
        (10, 11), # Udinese vs Monza
        (12, 13), # Genoa vs Lecce
        (14, 15), # Verona vs Cagliari
        (16, 17), # Empoli vs Parma
        (18, 19), # Como vs Venezia
    ]

    for i, (home_idx, away_idx) in enumerate(matchups):
        # Spread matches across weekend
        days_offset = (i // 3)  # 3 matches per day
        hours_offset = (i % 3) * 3  # 3 hours between matches
        match_date = base_date + timedelta(days=days_offset, hours=15 + hours_offset)

        fixture = models.Fixture(
            competition_id=competition.id,
            season="2025-2026",
            round="Giornata 19",
            match_date=match_date,
            home_team_id=teams[home_idx].id,
            away_team_id=teams[away_idx].id,
            status=models.FixtureStatus.SCHEDULED,
            external_id=10000 + i
        )
        session.add(fixture)
        fixtures.append(fixture)

    # Create some past results for Giornata 18
    past_date = datetime.now() - timedelta(days=7)
    past_results = [
        (0, 2, 2, 1),  # Inter 2-1 Juventus
        (1, 3, 1, 2),  # Milan 1-2 Napoli
        (4, 6, 3, 0),  # Roma 3-0 Atalanta
    ]

    for i, (home_idx, away_idx, home_score, away_score) in enumerate(past_results):
        fixture = models.Fixture(
            competition_id=competition.id,
            season="2025-2026",
            round="Giornata 18",
            match_date=past_date + timedelta(hours=i * 3),
            home_team_id=teams[home_idx].id,
            away_team_id=teams[away_idx].id,
            status=models.FixtureStatus.FINISHED,
            home_score=home_score,
            away_score=away_score,
            external_id=9000 + i
        )
        session.add(fixture)
        fixtures.append(fixture)

    await session.flush()
    return fixtures


async def main():
    """Main function to populate database"""
    print("🔄 Starting database population...")

    async with AsyncSessionLocal() as session:
        try:
            # Check if data already exists
            from sqlalchemy import select
            result = await session.execute(
                select(models.Competition).where(
                    models.Competition.season == "2025-2026"
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                print("⚠️  Data already exists for 2025-2026 season!")
                return

            # Create competition
            print("📊 Creating Serie A 2025-2026 competition...")
            competition = await create_competition(session)

            # Create teams
            print(f"⚽ Creating {len(SERIE_A_TEAMS)} Serie A teams...")
            teams = await create_teams(session)

            # Create fixtures
            print("📅 Creating sample fixtures...")
            fixtures = await create_fixtures(session, competition, teams)

            # Commit all changes
            await session.commit()

            print(f"\n✅ Success! Created:")
            print(f"   - 1 competition (Serie A 2025-2026)")
            print(f"   - {len(teams)} teams")
            print(f"   - {len(fixtures)} fixtures")
            print(f"\n🎉 Database is ready!")

        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(main())
