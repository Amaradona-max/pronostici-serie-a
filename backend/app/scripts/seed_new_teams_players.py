"""
Script to seed Sassuolo, Pisa, Cremonese players (Serie A 2025-2026)
Run with: python -m app.scripts.seed_new_teams_players
"""
import asyncio
import logging
from sqlalchemy import select
from app.db.engine import AsyncSessionLocal
from app.db.models import Team, Player

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NEW_TEAMS_PLAYERS = {
    "Sassuolo": [
        # Portieri
        {"name": "Arijanet Murić", "position": "Goalkeeper"},
        {"name": "Stefano Turati", "position": "Goalkeeper"},
        # Difensori
        {"name": "Tarik Muharemović", "position": "Defender"},
        {"name": "Jay Idzes", "position": "Defender"},
        {"name": "Fali Candé", "position": "Defender"},
        {"name": "Filippo Romagna", "position": "Defender"},
        {"name": "Josh Doig", "position": "Defender"},
        {"name": "Sebastian Walukiewicz", "position": "Defender"},
        {"name": "Woyo Coulibaly", "position": "Defender"},
        # Centrocampisti
        {"name": "Daniel Boloca", "position": "Midfielder"},
        {"name": "Luca Lipani", "position": "Midfielder"},
        {"name": "Nemanja Matić", "position": "Midfielder"},
        {"name": "Ismaël Koné", "position": "Midfielder"},
        {"name": "Kristian Thorstvedt", "position": "Midfielder"},
        {"name": "Aster Vranckx", "position": "Midfielder"},
        {"name": "Cristian Volpato", "position": "Midfielder"},
        # Attaccanti
        {"name": "Armand Laurienté", "position": "Forward"},
        {"name": "Alieu Fadera", "position": "Forward"},
        {"name": "Domenico Berardi", "position": "Forward"},
        {"name": "Andrea Pinamonti", "position": "Forward"},
        {"name": "Walid Cheddira", "position": "Forward"},
        {"name": "Luca Moro", "position": "Forward"},
    ],
    "Pisa": [
        # Portieri
        {"name": "Adrian Semper", "position": "Goalkeeper"},
        {"name": "Simone Scuffet", "position": "Goalkeeper"},
        # Difensori
        {"name": "Simone Canestrelli", "position": "Defender"},
        {"name": "Giovanni Bonfanti", "position": "Defender"},
        {"name": "Raúl Albiol", "position": "Defender"},
        {"name": "Arturo Calabresi", "position": "Defender"},
        {"name": "Antonio Caracciolo", "position": "Defender"},
        # Centrocampisti
        {"name": "Marius Marin", "position": "Midfielder"},
        {"name": "Malthe Højholt", "position": "Midfielder"},
        {"name": "Ebenezer Akinsanmiro", "position": "Midfielder"},
        {"name": "Michel Aebischer", "position": "Midfielder"},
        {"name": "Gabriele Piccinini", "position": "Midfielder"},
        {"name": "Idrissa Touré", "position": "Midfielder"},
        {"name": "Juan Cuadrado", "position": "Midfielder"},
        {"name": "Matteo Tramoni", "position": "Midfielder"},
        {"name": "Calvin Stengs", "position": "Midfielder"},
        {"name": "Stefano Moreo", "position": "Midfielder"},
        # Attaccanti
        {"name": "Louis Buffon", "position": "Forward"},
        {"name": "Mehdi Léris", "position": "Forward"},
        {"name": "M'Bala Nzola", "position": "Forward"},
        {"name": "Henrik Meister", "position": "Forward"},
    ],
    "Cremonese": [
        # Portieri
        {"name": "Emil Audero", "position": "Goalkeeper"},
        {"name": "Marco Silvestri", "position": "Goalkeeper"},
        # Difensori
        {"name": "Mikayil Faye", "position": "Defender"},
        {"name": "Federico Baschirotto", "position": "Defender"},
        {"name": "Matteo Bianchetti", "position": "Defender"},
        {"name": "Giuseppe Pezzella", "position": "Defender"},
        {"name": "Leonardo Sernicola", "position": "Defender"},
        {"name": "Filippo Terracciano", "position": "Defender"},
        {"name": "Tommaso Barbieri", "position": "Defender"},
        # Centrocampisti
        {"name": "Alberto Grassi", "position": "Midfielder"},
        {"name": "Warren Bondo", "position": "Midfielder"},
        {"name": "Martín Payero", "position": "Midfielder"},
        {"name": "Jari Vandeputte", "position": "Midfielder"},
        {"name": "Michele Collocolo", "position": "Midfielder"},
        {"name": "Alessio Zerbin", "position": "Midfielder"},
        {"name": "Franco Vázquez", "position": "Midfielder"},
        {"name": "Jeremy Sarmiento", "position": "Midfielder"},
        # Attaccanti
        {"name": "Faris Moumbagna", "position": "Forward"},
        {"name": "Antonio Sanabria", "position": "Forward"},
        {"name": "Federico Bonazzoli", "position": "Forward"},
        {"name": "Manuel De Luca", "position": "Forward"},
        {"name": "David Okereke", "position": "Forward"},
    ],
}

async def seed_new_teams_players():
    """Seed players for Sassuolo, Pisa, Cremonese"""
    async with AsyncSessionLocal() as db:
        total_players = 0
        
        for team_name, players_list in NEW_TEAMS_PLAYERS.items():
            stmt = select(Team).where(Team.name == team_name)
            result = await db.execute(stmt)
            team = result.scalar_one_or_none()
            
            if not team:
                logger.warning(f"Team {team_name} not found. Skipping.")
                continue
            
            logger.info(f"Seeding players for {team_name}...")
            
            for player_data in players_list:
                player = Player(
                    team_id=team.id,
                    name=player_data["name"],
                    position=player_data["position"]
                )
                db.add(player)
                total_players += 1
            
            await db.commit()
            logger.info(f"Completed seeding {len(players_list)} players for {team_name}")
        
        logger.info(f"✅ Successfully seeded {total_players} players for new teams")
        logger.info(f"🗓️  Saved at: 2025-12-31 13:00:00")

if __name__ == "__main__":
    asyncio.run(seed_new_teams_players())
