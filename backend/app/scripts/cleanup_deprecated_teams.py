import asyncio
from sqlalchemy import select, delete
from app.db.engine import AsyncSessionLocal
from app.db.models import Team, Player

DEPRECATED_TEAMS = ["Monza", "Venezia", "Empoli"]


async def cleanup():
    async with AsyncSessionLocal() as session:
        # Find deprecated teams
        result = await session.execute(select(Team).where(Team.name.in_(DEPRECATED_TEAMS)))
        teams = result.scalars().all()

        if not teams:
            print("✅ Nessuna squadra deprecata trovata")
            return

        # Delete players for these teams
        team_ids = [t.id for t in teams]
        await session.execute(delete(Player).where(Player.team_id.in_(team_ids)))

        # Delete the teams
        await session.execute(delete(Team).where(Team.id.in_(team_ids)))

        await session.commit()

        print(f"✅ Rimosse squadre deprecate: {', '.join([t.name for t in teams])}")


if __name__ == "__main__":
    asyncio.run(cleanup())
