import asyncio
import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.engine import AsyncSessionLocal
from app.db.models import Player, Team
from sqlalchemy import select
from sqlalchemy.orm import selectinload

async def verify_data():
    async with AsyncSessionLocal() as session:
        print("--- Verifying Roberto Piccoli ---")
        stmt = select(Player).options(selectinload(Player.team)).where(Player.name.ilike("%Piccoli%"))
        result = await session.execute(stmt)
        players = result.scalars().all()
        
        if not players:
            print("❌ Roberto Piccoli NOT FOUND in DB")
        else:
            for p in players:
                team_name = p.team.name if p.team else "No Team"
                print(f"✅ Found: {p.name} - Team: {team_name}")

        print("\n--- Verifying New Teams (2025/2026) ---")
        new_teams = ["Sassuolo", "Pisa", "Cremonese"]
        for t_name in new_teams:
            stmt = select(Team).where(Team.name == t_name)
            result = await session.execute(stmt)
            team = result.scalar_one_or_none()
            
            if not team:
                print(f"❌ Team {t_name} NOT FOUND")
            else:
                # Count players
                stmt_players = select(Player).where(Player.team_id == team.id)
                result_players = await session.execute(stmt_players)
                player_count = len(result_players.scalars().all())
                print(f"✅ Team {t_name} FOUND (ID: {team.id}) - Players count: {player_count}")

        print("\n--- Verifying Removed Teams ---")
        removed_teams = ["Monza", "Venezia", "Empoli"]
        for t_name in removed_teams:
            stmt = select(Team).where(Team.name == t_name)
            result = await session.execute(stmt)
            team = result.scalar_one_or_none()
            if team:
                print(f"⚠️ Warning: Deprecated Team {t_name} still exists in DB (ID: {team.id})")
            else:
                print(f"✅ Team {t_name} correctly removed/missing")

if __name__ == "__main__":
    asyncio.run(verify_data())
