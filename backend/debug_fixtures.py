
import asyncio
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.engine import AsyncSessionLocal
from app.models.models import Fixture

async def check_fixtures():
    async with AsyncSessionLocal() as db:
        stmt = select(Fixture).options(selectinload(Fixture.home_team), selectinload(Fixture.away_team)).where(Fixture.id.in_([1, 2]))
        result = await db.execute(stmt)
        fixtures = result.scalars().all()
        for f in fixtures:
            print(f"ID: {f.id}, Home: {f.home_team.name}, Away: {f.away_team.name}")

if __name__ == "__main__":
    asyncio.run(check_fixtures())
