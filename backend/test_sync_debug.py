"""
Test script to debug sync_live_data issues
This simulates what happens in GitHub Actions workflow
"""

import asyncio
import os
from datetime import datetime, timedelta, timezone

# Set environment variables
os.environ['FOOTBALL_DATA_KEY'] = '0b0926ead0f545c7bc196d8be1639b51'
os.environ['ENABLE_LIVE_UPDATES'] = 'true'

from app.services.providers.football_data import FootballDataAdapter

async def test_sync():
    """Test the sync process step by step"""

    print("=" * 70)
    print("🔍 DEBUG TEST - Sync Live Data")
    print("=" * 70)
    print()

    provider = FootballDataAdapter()

    try:
        # Step 1: Get all fixtures
        print("STEP 1: Fetching all Serie A fixtures...")
        all_fixtures = await provider.get_fixtures(135, "2025-2026")
        print(f"✅ Received {len(all_fixtures)} total fixtures")
        print()

        # Step 2: Filter for recent matches
        print("STEP 2: Filtering for recent matches (yesterday, today, tomorrow)...")
        today = datetime.now(timezone.utc)
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        print(f"   Today UTC: {today.isoformat()}")
        print(f"   Range: {yesterday.date()} to {tomorrow.date()}")
        print()

        recent_fixtures = [
            f for f in all_fixtures
            if yesterday <= f.match_date <= tomorrow
        ]

        print(f"✅ Found {len(recent_fixtures)} recent fixtures")
        print()

        # Step 3: Show fixture details
        if recent_fixtures:
            print("STEP 3: Recent fixtures details:")
            print()
            for i, fixture in enumerate(recent_fixtures, 1):
                print(f"   #{i} Fixture ID: {fixture.external_id}")
                print(f"       Home: {fixture.home_team_id}")
                print(f"       Away: {fixture.away_team_id}")
                print(f"       Score: {fixture.home_score} - {fixture.away_score}")
                print(f"       Status: {fixture.status}")
                print(f"       Date: {fixture.match_date}")
                print()
        else:
            print("❌ NO RECENT FIXTURES FOUND!")
            print()
            print("Showing first 5 fixtures from all:")
            for i, f in enumerate(all_fixtures[:5], 1):
                print(f"   #{i}: {f.match_date} - Status: {f.status}")
            print()

        # Step 4: Check specific matches
        print("STEP 4: Looking for specific matches (Cagliari-Milan, Como-Udinese)...")
        print()

        cagliari_milan = None
        como_udinese = None

        for f in all_fixtures:
            # Cagliari (104->490) vs Milan (98->489)
            if f.home_team_id == 490 and f.away_team_id == 489:
                cagliari_milan = f
            # Como (586->1047) vs Udinese (115->494)
            elif f.home_team_id == 1047 and f.away_team_id == 494:
                como_udinese = f

        if cagliari_milan:
            print("✅ CAGLIARI vs MILAN FOUND:")
            print(f"   External ID: {cagliari_milan.external_id}")
            print(f"   Home ID: {cagliari_milan.home_team_id} (should be 490)")
            print(f"   Away ID: {cagliari_milan.away_team_id} (should be 489)")
            print(f"   Score: {cagliari_milan.home_score} - {cagliari_milan.away_score}")
            print(f"   Status: {cagliari_milan.status}")
            print(f"   Date: {cagliari_milan.match_date}")

            # Check if in recent range
            if yesterday <= cagliari_milan.match_date <= tomorrow:
                print("   ✅ IN RECENT RANGE")
            else:
                print(f"   ❌ NOT IN RECENT RANGE (date is {cagliari_milan.match_date.date()})")
        else:
            print("❌ CAGLIARI vs MILAN NOT FOUND")

        print()

        if como_udinese:
            print("✅ COMO vs UDINESE FOUND:")
            print(f"   External ID: {como_udinese.external_id}")
            print(f"   Home ID: {como_udinese.home_team_id} (should be 1047)")
            print(f"   Away ID: {como_udinese.away_team_id} (should be 494)")
            print(f"   Score: {como_udinese.home_score} - {como_udinese.away_score}")
            print(f"   Status: {como_udinese.status}")
            print(f"   Date: {como_udinese.match_date}")

            # Check if in recent range
            if yesterday <= como_udinese.match_date <= tomorrow:
                print("   ✅ IN RECENT RANGE")
            else:
                print(f"   ❌ NOT IN RECENT RANGE (date is {como_udinese.match_date.date()})")
        else:
            print("❌ COMO vs UDINESE NOT FOUND")

        print()
        print("=" * 70)
        print("TEST COMPLETED")
        print("=" * 70)

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        await provider.close()

if __name__ == "__main__":
    asyncio.run(test_sync())
