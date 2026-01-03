#!/usr/bin/env python3
"""
Standalone script to fix external_ids - NO dependencies on app code
Can be run anywhere with just: DATABASE_URL=your_url python3 fix_db_standalone.py

This is a backup solution if GitHub Actions workflow doesn't work
"""

import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL environment variable not set")
    print("")
    print("Usage:")
    print("  DATABASE_URL='your_database_url' python3 fix_db_standalone.py")
    print("")
    sys.exit(1)

# Correct external IDs for all Serie A teams
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
    """Fix external_ids in the database"""

    print("=" * 70)
    print("🔧 FIX EXTERNAL IDS - Standalone Script")
    print("=" * 70)
    print()

    # Create engine
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            # Get all teams
            result = await session.execute(text("SELECT id, name, external_id FROM teams"))
            teams = result.fetchall()

            print(f"Found {len(teams)} teams in database")
            print()

            fixed_count = 0
            for team_id, team_name, current_external_id in teams:
                correct_id = CORRECT_EXTERNAL_IDS.get(team_name)

                if correct_id is None:
                    print(f"⚠️  Team '{team_name}' not in mapping - skipping")
                    continue

                if current_external_id != correct_id:
                    # Update external_id
                    await session.execute(
                        text("UPDATE teams SET external_id = :new_id WHERE id = :team_id"),
                        {"new_id": correct_id, "team_id": team_id}
                    )
                    fixed_count += 1
                    print(f"✅ Fixed: {team_name:20} {current_external_id} → {correct_id}")
                else:
                    print(f"✓  OK:    {team_name:20} external_id={correct_id}")

            if fixed_count > 0:
                await session.commit()
                print()
                print(f"✅ Fixed {fixed_count} teams - changes committed")
            else:
                print()
                print("✅ All teams already have correct external_ids")

            print()
            print("=" * 70)
            print("MIGRATION COMPLETED SUCCESSFULLY")
            print("=" * 70)
            print()
            print("Next: The sync script will now be able to find teams correctly!")
            print("Run the sync-live-data workflow or wait for scheduled run.")

        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(fix_external_ids())
