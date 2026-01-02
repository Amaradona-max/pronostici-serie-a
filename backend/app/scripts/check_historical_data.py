import asyncio
import sys
import os
from sqlalchemy import select, func

# Add parent directory to path (pointing to backend root)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.engine import AsyncSessionLocal
from app.db.models import MatchStats, TeamStats, Fixture, Competition

async def check_data():
    async with AsyncSessionLocal() as session:
        print("--- Checking Historical Data & xG ---")
        
        # Check Competitions
        stmt = select(Competition)
        result = await session.execute(stmt)
        competitions = result.scalars().all()
        print(f"Competitions: {len(competitions)}")
        for c in competitions:
            print(f" - {c.name} ({c.season})")

        # Check Fixtures count per season
        stmt = select(Fixture.season, func.count(Fixture.id)).group_by(Fixture.season)
        result = await session.execute(stmt)
        print("\nFixtures per season:")
        for season, count in result.all():
            print(f" - {season}: {count}")

        # Check MatchStats with xG
        stmt = select(func.count(MatchStats.id)).where(MatchStats.home_xg.isnot(None))
        result = await session.execute(stmt)
        xg_count = result.scalar()
        print(f"\nMatchStats with xG: {xg_count}")

        # Check TeamStats
        stmt = select(func.count(TeamStats.id))
        result = await session.execute(stmt)
        team_stats_count = result.scalar()
        print(f"TeamStats records: {team_stats_count}")

        # Sample xG data
        if xg_count > 0:
            stmt = select(MatchStats).where(MatchStats.home_xg.isnot(None)).limit(5)
            result = await session.execute(stmt)
            stats = result.scalars().all()
            print("\nSample xG data:")
            for s in stats:
                print(f" - Fixture {s.fixture_id}: Home xG {s.home_xg}, Away xG {s.away_xg}")

if __name__ == "__main__":
    asyncio.run(check_data())
