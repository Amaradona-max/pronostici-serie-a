"""
Migration script to fix external_ids in the database

This script ensures all teams have the correct external_ids
that match the team mapping in football_data.py

Run with: python -m app.scripts.fix_external_ids
"""

import asyncio
import logging
from sqlalchemy import select, update

from app.db.engine import AsyncSessionLocal
from app.db.models import Team

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Correct external IDs for all Serie A teams (from seed_teams.py)
CORRECT_EXTERNAL_IDS = {
    "Inter": 505,
    "AC Milan": 489,
    "Juventus": 496,
    "Napoli": 492,
    "AS Roma": 497,
    "Lazio": 487,
    "Atalanta": 499,
    "Fiorentina": 502,
    "Bologna": 500,
    "Torino": 503,
    "Udinese": 494,
    "Lecce": 867,
    "Cagliari": 490,
    "Hellas Verona": 504,
    "Genoa": 495,
    "Parma": 130,
    "Como": 1047,
    "Sassuolo": 488,
    "Pisa": 506,
    "Cremonese": 520,
}


async def fix_external_ids():
    """Fix external_ids for all teams"""

    logger.info("=" * 70)
    logger.info("🔧 FIX EXTERNAL IDS - Migration Script")
    logger.info("=" * 70)
    logger.info("")

    async with AsyncSessionLocal() as session:
        try:
            # Get all teams
            stmt = select(Team)
            result = await session.execute(stmt)
            teams = result.scalars().all()

            logger.info(f"Found {len(teams)} teams in database")
            logger.info("")

            fixed_count = 0
            for team in teams:
                correct_id = CORRECT_EXTERNAL_IDS.get(team.name)

                if correct_id is None:
                    logger.warning(f"⚠️  Team '{team.name}' not in mapping - skipping")
                    continue

                if team.external_id != correct_id:
                    old_id = team.external_id
                    team.external_id = correct_id
                    fixed_count += 1
                    logger.info(f"✅ Fixed: {team.name:20} {old_id} → {correct_id}")
                else:
                    logger.info(f"✓  OK:    {team.name:20} external_id={correct_id}")

            if fixed_count > 0:
                await session.commit()
                logger.info("")
                logger.info(f"✅ Fixed {fixed_count} teams - changes committed")
            else:
                logger.info("")
                logger.info("✅ All teams already have correct external_ids")

            logger.info("")
            logger.info("=" * 70)
            logger.info("MIGRATION COMPLETED SUCCESSFULLY")
            logger.info("=" * 70)

        except Exception as e:
            logger.error(f"❌ Migration failed: {str(e)}")
            raise


if __name__ == "__main__":
    asyncio.run(fix_external_ids())
