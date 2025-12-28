"""
Script to seed Serie A teams into database
Run with: python -m app.scripts.seed_teams
"""

import asyncio
import logging
from sqlalchemy import select

from app.db.engine import AsyncSessionLocal
from app.db.models import Team, Stadium, Competition

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERIE_A_TEAMS = [
    {"name": "Inter", "external_id": 505, "stadium": "San Siro", "city": "Milano"},
    {"name": "AC Milan", "external_id": 489, "stadium": "San Siro", "city": "Milano"},
    {"name": "Juventus", "external_id": 496, "stadium": "Allianz Stadium", "city": "Torino"},
    {"name": "Napoli", "external_id": 492, "stadium": "Diego Armando Maradona", "city": "Napoli"},
    {"name": "AS Roma", "external_id": 497, "stadium": "Olimpico", "city": "Roma"},
    {"name": "Lazio", "external_id": 487, "stadium": "Olimpico", "city": "Roma"},
    {"name": "Atalanta", "external_id": 499, "stadium": "Gewiss Stadium", "city": "Bergamo"},
    {"name": "Fiorentina", "external_id": 502, "stadium": "Artemio Franchi", "city": "Firenze"},
    {"name": "Bologna", "external_id": 500, "stadium": "Renato Dall'Ara", "city": "Bologna"},
    {"name": "Torino", "external_id": 503, "stadium": "Olimpico Grande Torino", "city": "Torino"},
    {"name": "Udinese", "external_id": 494, "stadium": "Dacia Arena", "city": "Udine"},
    {"name": "Empoli", "external_id": 511, "stadium": "Carlo Castellani", "city": "Empoli"},
    {"name": "Sassuolo", "external_id": 488, "stadium": "Mapei Stadium", "city": "Reggio Emilia"},
    {"name": "Cagliari", "external_id": 490, "stadium": "Unipol Domus", "city": "Cagliari"},
    {"name": "Verona", "external_id": 504, "stadium": "Bentegodi", "city": "Verona"},
    {"name": "Lecce", "external_id": 867, "stadium": "Via del Mare", "city": "Lecce"},
    {"name": "Monza", "external_id": 1579, "stadium": "U-Power Stadium", "city": "Monza"},
    {"name": "Salernitana", "external_id": 514, "stadium": "Arechi", "city": "Salerno"},
    {"name": "Como", "external_id": 512, "stadium": "Giuseppe Sinigaglia", "city": "Como"},
    {"name": "Parma", "external_id": 491, "stadium": "Ennio Tardini", "city": "Parma"},
]


async def seed_teams():
    """Seed Serie A teams and stadiums"""
    async with AsyncSessionLocal() as session:
        logger.info("Starting teams and stadiums seeding...")

        # Create competition
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
            logger.info("Created Serie A competition")

        for team_data in SERIE_A_TEAMS:
            # Check if team exists
            stmt = select(Team).where(Team.external_id == team_data["external_id"])
            existing_team = (await session.execute(stmt)).scalar_one_or_none()

            if existing_team:
                logger.info(f"Team {team_data['name']} already exists, skipping")
                continue

            # Create or get stadium
            stadium_stmt = select(Stadium).where(Stadium.name == team_data["stadium"])
            stadium = (await session.execute(stadium_stmt)).scalar_one_or_none()

            if not stadium:
                stadium = Stadium(
                    name=team_data["stadium"],
                    city=team_data["city"],
                    home_advantage_factor=1.15  # Default home advantage
                )
                session.add(stadium)
                await session.flush()

            # Create team
            new_team = Team(
                name=team_data["name"],
                short_name=team_data["name"][:3].upper(),
                stadium_name=team_data["stadium"],
                external_id=team_data["external_id"],
                elo_rating=1500.0  # Default ELO
            )
            session.add(new_team)

            logger.info(f"Created team: {team_data['name']}")

        await session.commit()
        logger.info("✅ Teams and stadiums seeding completed!")


if __name__ == "__main__":
    asyncio.run(seed_teams())
