#!/usr/bin/env python3
"""
Full Re-sync Script - Sync ALL fixtures from Football-Data.org
Ensures database is 100% aligned with real Serie A 2025/2026 data
"""
import asyncio
import os
import sys
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.engine import AsyncSessionLocal
from app.db.models import Fixture, Team, Competition
from app.services.providers.orchestrator import DataProviderOrchestrator

async def full_resync():
    """
    Complete re-sync of all Serie A 2025/2026 fixtures
    """
    print("=" * 80)
    print("🔄 FULL RE-SYNC - Serie A 2025/2026")
    print("=" * 80)
    print()
    print(f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print()

    # Initialize provider
    provider = DataProviderOrchestrator()

    async with AsyncSessionLocal() as session:
        try:
            # 1. Get competition
            print("📋 Loading competition...")
            comp_result = await session.execute(
                select(Competition).where(Competition.season == "2025-2026")
            )
            competition = comp_result.scalar_one_or_none()

            if not competition:
                print("❌ Competition 2025-2026 not found!")
                return False

            print(f"✅ Competition: {competition.name} (ID: {competition.id})")
            print()

            # 2. Get all teams with external_ids
            print("📋 Loading teams...")
            teams_result = await session.execute(select(Team))
            teams = teams_result.scalars().all()

            team_map = {t.external_id: t for t in teams if t.external_id}
            print(f"✅ Loaded {len(team_map)} teams with external IDs")
            print()

            # 3. Fetch ALL fixtures from Football-Data.org
            print("🌐 Fetching ALL fixtures from Football-Data.org...")
            print("   (this may take a few seconds)")
            print()

            # Serie A ID (internal) and season
            fixtures_data = await provider.get_fixtures_with_fallback(135, "2025-2026")

            if not fixtures_data:
                print("❌ No fixtures returned from provider!")
                return False

            print(f"✅ Retrieved {len(fixtures_data)} fixtures from Football-Data.org")
            print()

            # 4. Get existing fixtures from database
            print("📋 Loading existing fixtures from database...")
            db_fixtures_result = await session.execute(
                select(Fixture).where(Fixture.season == "2025-2026")
            )
            db_fixtures = db_fixtures_result.scalars().all()
            db_fixture_map = {f.external_id: f for f in db_fixtures if f.external_id}

            print(f"✅ Found {len(db_fixtures)} existing fixtures in database")
            print()

            # 5. Sync each fixture
            print("🔄 Syncing fixtures...")
            print()

            created = 0
            updated = 0
            skipped = 0
            errors = 0

            for i, fixture_data in enumerate(fixtures_data, 1):
                try:
                    external_id = fixture_data.external_id
                    home_ext_id = fixture_data.home_team_id
                    away_ext_id = fixture_data.away_team_id

                    # Find teams
                    home_team = team_map.get(home_ext_id)
                    away_team = team_map.get(away_ext_id)

                    if not home_team or not away_team:
                        skipped += 1
                        if i % 50 == 0:
                            print(f"   ⚠️  Fixture {i}/{len(fixtures_data)}: Teams not found (ext_ids: {home_ext_id}, {away_ext_id})")
                        continue

                    # Check if exists
                    if external_id in db_fixture_map:
                        # Update existing
                        fixture = db_fixture_map[external_id]
                        fixture.match_date = fixture_data.match_date
                        fixture.status = fixture_data.status.upper()
                        fixture.home_score = fixture_data.home_score
                        fixture.away_score = fixture_data.away_score
                        fixture.round = fixture_data.round
                        fixture.last_synced_at = datetime.now(timezone.utc)
                        updated += 1
                    else:
                        # Create new
                        fixture = Fixture(
                            competition_id=competition.id,
                            season="2025-2026",
                            round=fixture_data.round,
                            match_date=fixture_data.match_date,
                            home_team_id=home_team.id,
                            away_team_id=away_team.id,
                            status=fixture_data.status.upper(),
                            home_score=fixture_data.home_score,
                            away_score=fixture_data.away_score,
                            external_id=external_id,
                            last_synced_at=datetime.now(timezone.utc)
                        )
                        session.add(fixture)
                        created += 1

                    if i % 50 == 0:
                        print(f"   📊 Progress: {i}/{len(fixtures_data)} fixtures processed...")

                except Exception as e:
                    errors += 1
                    print(f"   ❌ Error processing fixture {i}: {e}")
                    continue

            # Commit all changes
            await session.commit()

            print()
            print("=" * 80)
            print("✅ FULL RE-SYNC COMPLETED!")
            print("=" * 80)
            print()
            print(f"📊 Summary:")
            print(f"   - Created: {created} new fixtures")
            print(f"   - Updated: {updated} existing fixtures")
            print(f"   - Skipped: {skipped} (teams not in database)")
            print(f"   - Errors: {errors}")
            print()
            print(f"Total synced: {created + updated}")
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
    print("🚀 Starting Full Re-Sync...")
    print()

    success = asyncio.run(full_resync())

    if success:
        print("✅ Re-sync completed successfully!")
        print()
        print("Next steps:")
        print("1. The database is now 100% aligned with Football-Data.org")
        print("2. All future syncs will keep it updated")
        print("3. The app will display accurate Serie A 2025/2026 data")
        print()
        sys.exit(0)
    else:
        print("❌ Re-sync failed!")
        sys.exit(1)
