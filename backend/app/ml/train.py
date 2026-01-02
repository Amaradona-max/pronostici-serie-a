
import logging
import asyncio
import os
import sys
from datetime import datetime
from typing import List, Dict
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

# Add parent directory to path to allow imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.engine import AsyncSessionLocal
from app.db.models import Fixture, MatchStats
from app.ml.dixon_coles import DixonColesModel

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "saved_models", "dixon_coles_latest.pkl")

class TrainingPipeline:
    """
    Pipeline for training the Dixon-Coles model on historical data.
    """
    
    def __init__(self):
        self.model = DixonColesModel()
        
    async def fetch_training_data(self) -> List[Dict]:
        """Fetch finished matches with xG data from DB"""
        async with AsyncSessionLocal() as session:
            # Fetch finished fixtures with match stats
            stmt = select(Fixture).options(
                selectinload(Fixture.match_stats),
                selectinload(Fixture.home_team),
                selectinload(Fixture.away_team)
            ).where(
                and_(
                    Fixture.status == 'finished',
                    Fixture.home_score.isnot(None),
                    Fixture.away_score.isnot(None)
                )
            ).order_by(Fixture.match_date.asc())
            
            fixtures = (await session.execute(stmt)).scalars().all()
            
            training_data = []
            xg_count = 0
            
            for f in fixtures:
                match_data = {
                    'home_team': f.home_team.name,
                    'away_team': f.away_team.name,
                    'home_score': f.home_score,
                    'away_score': f.away_score,
                    'date': f.match_date
                }
                
                # Add xG if available
                if f.match_stats and f.match_stats.home_xg is not None:
                    match_data['home_xg'] = f.match_stats.home_xg
                    match_data['away_xg'] = f.match_stats.away_xg
                    xg_count += 1
                
                training_data.append(match_data)
                
            logger.info(f"Fetched {len(training_data)} matches. {xg_count} have xG data.")
            return training_data, xg_count > 0

    async def run(self):
        """Run the full training pipeline"""
        logger.info("Starting training pipeline...")
        
        matches, has_xg = await self.fetch_training_data()
        
        if not matches:
            logger.warning("No matches found for training.")
            return
            
        # Ensure directory exists
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        
        # Fit model
        if has_xg:
            logger.info("Training with Expected Goals (xG)...")
            self.model.fit_xg(matches)
        else:
            logger.info("Training with Actual Goals (Standard Dixon-Coles)...")
            self.model.fit(matches)
            
        # Save model
        self.model.save(MODEL_PATH)
        logger.info(f"Model saved to {MODEL_PATH}")
        
        # Print some stats
        print(f"Training completed.")
        print(f"Teams: {len(self.model.team_list)}")
        print(f"Home Advantage: {self.model.home_advantage:.3f}")
        
        # Print top 5 attacking teams
        sorted_attack = sorted(self.model.attack_params.items(), key=lambda x: x[1], reverse=True)
        print("\nTop 5 Attacking Teams:")
        for team, strength in sorted_attack[:5]:
            print(f"{team}: {strength:.3f}")

if __name__ == "__main__":
    # Setup basic logging
    logging.basicConfig(level=logging.INFO)
    
    pipeline = TrainingPipeline()
    asyncio.run(pipeline.run())
