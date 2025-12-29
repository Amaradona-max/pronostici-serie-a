"""
Admin API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import logging

from app.db.engine import get_db
from app.db import models

logger = logging.getLogger(__name__)
router = APIRouter()


# Serie A teams 2025-2026 (Official lineup)
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
    {"name": "Genoa", "short_name": "GEN", "code": "GEN", "external_id": 495},
    {"name": "Lecce", "short_name": "LEC", "code": "LEC", "external_id": 867},
    {"name": "Hellas Verona", "short_name": "VER", "code": "VER", "external_id": 504},
    {"name": "Cagliari", "short_name": "CAG", "code": "CAG", "external_id": 490},
    {"name": "Parma", "short_name": "PAR", "code": "PAR", "external_id": 1037},
    {"name": "Como", "short_name": "COM", "code": "COM", "external_id": 512},
    # Neopromosse 2025/2026
    {"name": "Cremonese", "short_name": "CRE", "code": "CRE", "external_id": 445},
    {"name": "Pisa", "short_name": "PIS", "code": "PIS", "external_id": 1071},
    {"name": "Sassuolo", "short_name": "SAS", "code": "SAS", "external_id": 488},
]


@router.post("/reset-database", summary="Reset and repopulate database")
async def reset_database(db: AsyncSession = Depends(get_db)):
    """
    Delete all existing data and repopulate with fresh sample data.
    USE WITH CAUTION - deletes all data!
    """
    try:
        logger.info("Resetting database...")

        # Delete all fixtures, teams, competitions
        from sqlalchemy import delete

        await db.execute(delete(models.Fixture))
        await db.execute(delete(models.Team))
        await db.execute(delete(models.Competition))
        await db.commit()

        logger.info("Database cleared, now repopulating...")

        # Call the populate function
        return await populate_sample_data(db)

    except Exception as e:
        await db.rollback()
        logger.error(f"Error resetting database: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/populate-sample-data", summary="Populate database with sample data")
async def populate_sample_data(db: AsyncSession = Depends(get_db)):
    """
    Populate database with sample Serie A data.
    This endpoint can be called once to initialize the database.
    """
    try:
        logger.info("Starting database population...")

        # Check if data already exists
        result = await db.execute(
            select(models.Competition).where(
                models.Competition.season == "2025-2026"
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Data already exists for 2025-2026 season"
            )

        # Create competition
        logger.info("Creating Serie A 2025-2026 competition...")
        competition = models.Competition(
            name="Serie A",
            country="Italy",
            season="2025-2026",
            external_id=135
        )
        db.add(competition)
        await db.flush()

        # Create teams
        logger.info(f"Creating {len(SERIE_A_TEAMS)} Serie A teams...")
        teams = []
        for team_data in SERIE_A_TEAMS:
            team = models.Team(**team_data)
            db.add(team)
            teams.append(team)

        await db.flush()

        # Create fixtures
        logger.info("Creating sample fixtures...")
        fixtures = []

        # Giornata 19: weekend 3-5 gennaio 2026
        # Sabato 4 gennaio 2026, ore 15:00 (primo slot)
        base_date = datetime(2026, 1, 4, 15, 0, 0)

        # Create fixtures for Giornata 19 (upcoming)
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
            days_offset = (i // 3)
            hours_offset = (i % 3) * 3
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
            db.add(fixture)
            fixtures.append(fixture)

        # Create some past results for Giornata 18
        # Weekend 21-22 dicembre 2025
        # Sabato 21 dicembre 2025, ore 15:00
        past_date = datetime(2025, 12, 21, 15, 0, 0)

        past_results = [
            (0, 2, 2, 1),  # Inter 2-1 Juventus
            (1, 3, 1, 2),  # Milan 1-2 Napoli
            (4, 6, 3, 0),  # Roma 3-0 Atalanta
            (5, 7, 2, 2),  # Lazio 2-2 Fiorentina
            (8, 10, 1, 0), # Bologna 1-0 Udinese
        ]

        for i, (home_idx, away_idx, home_score, away_score) in enumerate(past_results):
            # Spread matches across the weekend
            match_time = past_date + timedelta(days=i // 3, hours=(i % 3) * 3)

            fixture = models.Fixture(
                competition_id=competition.id,
                season="2025-2026",
                round="Giornata 18",
                match_date=match_time,
                home_team_id=teams[home_idx].id,
                away_team_id=teams[away_idx].id,
                status=models.FixtureStatus.FINISHED,
                home_score=home_score,
                away_score=away_score,
                external_id=9000 + i
            )
            db.add(fixture)
            fixtures.append(fixture)

        # Commit all changes
        await db.commit()

        logger.info(f"✅ Successfully populated database!")

        return {
            "message": "Database populated successfully",
            "competition": competition.name,
            "season": competition.season,
            "teams_created": len(teams),
            "fixtures_created": len(fixtures),
            "scheduled_fixtures": len(matchups),
            "finished_fixtures": len(past_results)
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error populating database: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
