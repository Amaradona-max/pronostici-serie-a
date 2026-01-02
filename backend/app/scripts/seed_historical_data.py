
import asyncio
import logging
import random
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.engine import AsyncSessionLocal
from app.db.models import Fixture, MatchStats, Team, Competition
from sqlalchemy import select

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Serie A Teams 2024/25 (Approximate strengths for simulation)
TEAMS = {
    "Inter": {"att": 2.2, "def": 0.8},
    "Milan": {"att": 1.9, "def": 1.1},
    "Juventus": {"att": 1.7, "def": 0.7},
    "Atalanta": {"att": 2.0, "def": 1.2},
    "Napoli": {"att": 1.8, "def": 1.0},
    "Roma": {"att": 1.6, "def": 1.1},
    "Lazio": {"att": 1.5, "def": 1.0},
    "Fiorentina": {"att": 1.4, "def": 1.1},
    "Torino": {"att": 1.1, "def": 1.0},
    "Bologna": {"att": 1.3, "def": 1.1},
    "Monza": {"att": 1.0, "def": 1.2},
    "Genoa": {"att": 1.0, "def": 1.3},
    "Lecce": {"att": 0.9, "def": 1.4},
    "Udinese": {"att": 0.9, "def": 1.3},
    "Empoli": {"att": 0.8, "def": 1.4},
    "Verona": {"att": 0.9, "def": 1.5},
    "Cagliari": {"att": 0.9, "def": 1.5},
    "Salernitana": {"att": 0.7, "def": 1.8}, # Replaced by Parma/Como/Venezia in reality but using placeholder
    "Frosinone": {"att": 0.8, "def": 1.7},
    "Sassuolo": {"att": 1.2, "def": 1.6}
}

async def seed_historical_matches():
    async with AsyncSessionLocal() as session:
        # Get competition
        stmt = select(Competition).where(Competition.name == "Serie A")
        competition = (await session.execute(stmt)).scalar_one_or_none()
        
        if not competition:
            logger.error("Serie A competition not found. Run basic seed first.")
            return

        # Get teams
        stmt = select(Team)
        teams_db = (await session.execute(stmt)).scalars().all()
        team_map = {t.name: t for t in teams_db}

        # Simulate 17 rounds
        start_date = datetime(2025, 8, 20) # Start of season
        
        matches_created = 0
        
        for round_num in range(1, 18):
            round_date = start_date + timedelta(weeks=round_num-1)
            
            # Create pairings (simplified round robin)
            team_names = list(team_map.keys())
            random.shuffle(team_names)
            
            for i in range(0, len(team_names), 2):
                if i+1 >= len(team_names): break
                
                home_name = team_names[i]
                away_name = team_names[i+1]
                
                if home_name not in TEAMS: TEAMS[home_name] = {"att": 1.0, "def": 1.0}
                if away_name not in TEAMS: TEAMS[away_name] = {"att": 1.0, "def": 1.0}
                
                home_team = team_map[home_name]
                away_team = team_map[away_name]
                
                # Simulate Score using Poisson
                home_str = TEAMS[home_name]
                away_str = TEAMS[away_name]
                
                # Lambda/Mu
                home_exp = home_str['att'] * away_str['def'] * 1.2 # Home adv
                away_exp = away_str['att'] * home_str['def']
                
                import numpy as np
                home_goals = np.random.poisson(home_exp)
                away_goals = np.random.poisson(away_exp)
                
                # Simulate xG (correlated with goals but not identical)
                home_xg = max(0.1, np.random.normal(home_exp, 0.4))
                away_xg = max(0.1, np.random.normal(away_exp, 0.4))
                
                # Create Fixture
                fixture = Fixture(
                    competition_id=competition.id,
                    season="2025-2026",
                    round=f"Giornata {round_num}",
                    match_date=round_date + timedelta(hours=random.randint(12, 20)),
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    status="finished",
                    home_score=home_goals,
                    away_score=away_goals,
                    external_id=random.randint(100000, 999999)
                )
                session.add(fixture)
                await session.flush() # Get ID
                
                # Create MatchStats
                stats = MatchStats(
                    fixture_id=fixture.id,
                    home_xg=round(home_xg, 2),
                    away_xg=round(away_xg, 2),
                    home_possession=50,
                    away_possession=50
                )
                session.add(stats)
                matches_created += 1
                
        await session.commit()
        logger.info(f"Seeded {matches_created} historical matches with xG.")

if __name__ == "__main__":
    asyncio.run(seed_historical_matches())
