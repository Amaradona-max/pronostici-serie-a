#!/usr/bin/env python3
"""
Add missing columns to team_stats table
"""
import asyncio
import sys
import os
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.engine import AsyncSessionLocal


async def migrate():
    """
    Add position, goal_difference, and points columns to team_stats
    """
    print("=" * 80)
    print("🔧 MIGRATING TEAM_STATS TABLE")
    print("=" * 80)
    print()

    async with AsyncSessionLocal() as session:
        try:
            # Check if columns exist
            print("📋 Checking existing columns...")
            result = await session.execute(text("PRAGMA table_info(team_stats)"))
            columns = {row[1] for row in result.fetchall()}
            print(f"✅ Found columns: {sorted(columns)}")
            print()

            migrations_needed = []
            if "position" not in columns:
                migrations_needed.append("position")
            if "goal_difference" not in columns:
                migrations_needed.append("goal_difference")
            if "points" not in columns:
                migrations_needed.append("points")

            if not migrations_needed:
                print("✅ All columns already exist!")
                return True

            print(f"🔧 Need to add columns: {migrations_needed}")
            print()

            # Add missing columns
            for column in migrations_needed:
                print(f"   Adding {column}...")
                if column == "position":
                    await session.execute(text(
                        "ALTER TABLE team_stats ADD COLUMN position INTEGER"
                    ))
                elif column == "goal_difference":
                    await session.execute(text(
                        "ALTER TABLE team_stats ADD COLUMN goal_difference INTEGER DEFAULT 0"
                    ))
                elif column == "points":
                    await session.execute(text(
                        "ALTER TABLE team_stats ADD COLUMN points INTEGER DEFAULT 0"
                    ))

            await session.commit()
            print()
            print("=" * 80)
            print("✅ MIGRATION COMPLETED!")
            print("=" * 80)
            print()
            return True

        except Exception as e:
            print()
            print("=" * 80)
            print(f"❌ ERROR: {e}")
            print("=" * 80)
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    print()
    success = asyncio.run(migrate())

    if success:
        print("✅ Migration successful!")
        print()
        sys.exit(0)
    else:
        print("❌ Migration failed!")
        sys.exit(1)
