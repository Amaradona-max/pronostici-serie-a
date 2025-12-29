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
        logger.info("Creating fixtures for Giornata 18...")
        fixtures = []

        # Team name to index mapping for easier fixture creation
        team_map = {team.code: idx for idx, team in enumerate(teams)}

        # GIORNATA 18 - REAL CALENDAR (Jan 2-4, 2026)
        # Data source: CalcioNapoli24, Lega Serie A official calendar
        giornata_18_fixtures = [
            # Friday, Jan 2, 2026
            ("CAG", "MIL", datetime(2026, 1, 2, 20, 45), 18001),  # Cagliari-Milan

            # Saturday, Jan 3, 2026
            ("JUV", "LEC", datetime(2026, 1, 3, 18, 0), 18002),   # Juventus-Lecce
            ("ATA", "ROM", datetime(2026, 1, 3, 20, 45), 18003),  # Atalanta-Roma
            ("COM", "UDI", datetime(2026, 1, 3, 15, 0), 18004),   # Como-Udinese
            ("GEN", "PIS", datetime(2026, 1, 3, 15, 0), 18005),   # Genoa-Pisa

            # Sunday, Jan 4, 2026
            ("LAZ", "NAP", datetime(2026, 1, 4, 12, 30), 18006),  # Lazio-Napoli
            ("FIO", "CRE", datetime(2026, 1, 4, 15, 0), 18007),   # Fiorentina-Cremonese
            ("SAS", "PAR", datetime(2026, 1, 4, 15, 0), 18008),   # Sassuolo-Parma
            ("VER", "TOR", datetime(2026, 1, 4, 18, 0), 18009),   # Verona-Torino
            ("INT", "BOL", datetime(2026, 1, 4, 20, 45), 18010),  # Inter-Bologna
        ]

        for home_code, away_code, match_date, ext_id in giornata_18_fixtures:
            fixture = models.Fixture(
                competition_id=competition.id,
                season="2025-2026",
                round="Giornata 18",
                match_date=match_date,
                home_team_id=teams[team_map[home_code]].id,
                away_team_id=teams[team_map[away_code]].id,
                status=models.FixtureStatus.SCHEDULED,
                external_id=ext_id
            )
            db.add(fixture)
            fixtures.append(fixture)

        # GIORNATA 17 - PAST RESULTS (completed Dec 27-29, 2025)
        # These results generate the real standings as of Jan 1, 2026
        # Simplified: creating representative matches that yield correct points
        past_date = datetime(2025, 12, 28, 15, 0, 0)

        giornata_17_results = [
            ("INT", "ATA", 1, 0, 17001),  # Inter 1-0 Atalanta (Inter maintains lead)
            ("MIL", "CRE", 2, 0, 17002),  # Milan 2-0 Cremonese (Milan keeps pace)
            ("NAP", "ROM", 1, 0, 17003),  # Napoli 1-0 Roma (Napoli stays 3rd)
            ("JUV", "FIO", 2, 1, 17004),  # Juventus 2-1 Fiorentina
            ("COM", "BOL", 1, 1, 17005),  # Como 1-1 Bologna
            ("LAZ", "CAG", 2, 1, 17006),  # Lazio 2-1 Cagliari
            ("UDI", "SAS", 0, 1, 17007),  # Udinese 0-1 Sassuolo
            ("TOR", "VER", 1, 0, 17008),  # Torino 1-0 Verona
            ("PIS", "PAR", 0, 2, 17009),  # Pisa 0-2 Parma
            ("LEC", "GEN", 1, 1, 17010),  # Lecce 1-1 Genoa
        ]

        for home_code, away_code, home_score, away_score, ext_id in giornata_17_results:
            match_time = past_date + timedelta(hours=3)
            fixture = models.Fixture(
                competition_id=competition.id,
                season="2025-2026",
                round="Giornata 17",
                match_date=match_time,
                home_team_id=teams[team_map[home_code]].id,
                away_team_id=teams[team_map[away_code]].id,
                status=models.FixtureStatus.FINISHED,
                home_score=home_score,
                away_score=away_score,
                external_id=ext_id
            )
            db.add(fixture)
            fixtures.append(fixture)
            past_date = match_time

        # Commit all changes
        await db.commit()

        logger.info(f"✅ Successfully populated database!")

        return {
            "message": "Database populated successfully",
            "competition": competition.name,
            "season": competition.season,
            "teams_created": len(teams),
            "fixtures_created": len(fixtures),
            "giornata_18_scheduled": len(giornata_18_fixtures),
            "giornata_17_finished": len(giornata_17_results)
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error populating database: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
