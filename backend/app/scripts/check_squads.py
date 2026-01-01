
import asyncio
import logging
from sqlalchemy import select
from app.db.engine import AsyncSessionLocal
from app.db.models import Player, Team

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_squads():
    async with AsyncSessionLocal() as db:
        # Get all teams
        result = await db.execute(select(Team).order_by(Team.name))
        teams = result.scalars().all()

        if not teams:
            logger.error("No teams found!")
            return

        logger.info(f"Checking squads for {len(teams)} teams...")

        total_players = 0
        for team in teams:
            # Get players for team
            result = await db.execute(select(Player).where(Player.team_id == team.id).order_by(Player.name))
            players = result.scalars().all()
            
            logger.info(f"=== {team.name} ({len(players)} players) ===")
            for player in players:
                logger.info(f"- {player.name} ({player.position})")
            
            total_players += len(players)

        logger.info(f"Total players in DB: {total_players}")

        # Check for duplicates (same name in multiple teams? Schema usually prevents it but good to check if unique constraint missing)
        # Actually duplicate names might exist (different people), but strict duplicates (same person) shouldn't if we use name as key.
        
        # Check specifically for Piccoli
        result = await db.execute(select(Player).where(Player.name.like("%Piccoli%")))
        piccolis = result.scalars().all()
        for p in piccolis:
             # Fetch team name
             t_res = await db.execute(select(Team).where(Team.id == p.team_id))
             t = t_res.scalars().first()
             t_name = t.name if t else "Unknown"
             logger.info(f"Found Piccoli: {p.name} in {t_name}")

if __name__ == "__main__":
    asyncio.run(check_squads())
