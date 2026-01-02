
"""
Script to seed realistic predictions for all fixtures
Populates predictions table with data from the trained Dixon-Coles model
Run with: python -m app.scripts.seed_predictions
"""

import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.engine import AsyncSessionLocal
from app.db.models import Fixture, Prediction
from app.ml.dixon_coles import DixonColesModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "saved_models", "dixon_coles_latest.pkl")

async def seed_predictions():
    """
    Generate predictions for all scheduled fixtures using the trained model.
    """
    logger.info("Starting prediction seeding...")

    # Load Model
    if not os.path.exists(MODEL_PATH):
        logger.error(f"Trained model not found at {MODEL_PATH}. Run training first.")
        return
        
    try:
        model = DixonColesModel.load(MODEL_PATH)
        logger.info(f"Loaded model version 1.2.0-xg (Home Adv: {model.home_advantage:.3f})")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return

    async with AsyncSessionLocal() as session:
        # Get all scheduled fixtures
        stmt = select(Fixture).options(
            selectinload(Fixture.home_team),
            selectinload(Fixture.away_team)
        ).where(
            Fixture.status == 'scheduled'
        )
        fixtures = (await session.execute(stmt)).scalars().all()
        
        logger.info(f"Found {len(fixtures)} scheduled fixtures.")
        
        predictions_created = 0
        predictions_updated = 0
        
        for fixture in fixtures:
            # Check if prediction exists
            pred_stmt = select(Prediction).where(Prediction.fixture_id == fixture.id)
            existing_pred = (await session.execute(pred_stmt)).scalar_one_or_none()
            
            try:
                # Generate prediction
                # In a real scenario, we would calculate form factors dynamically
                # Here we assume standard form (1.0) or could randomize slightly
                pred_data = model.predict_match(
                    fixture.home_team.name,
                    fixture.away_team.name
                )
                
                confidence = max(pred_data['prob_home_win'], pred_data['prob_draw'], pred_data['prob_away_win'])
                
                if existing_pred:
                    # Update existing
                    existing_pred.prob_home_win = pred_data['prob_home_win']
                    existing_pred.prob_draw = pred_data['prob_draw']
                    existing_pred.prob_away_win = pred_data['prob_away_win']
                    existing_pred.prob_over_25 = pred_data['prob_over_25']
                    existing_pred.prob_under_25 = pred_data['prob_under_25']
                    existing_pred.prob_btts_yes = pred_data['prob_btts_yes']
                    existing_pred.prob_btts_no = pred_data['prob_btts_no']
                    existing_pred.most_likely_score = pred_data['most_likely_score']
                    existing_pred.confidence_score = confidence
                    existing_pred.expected_home_goals = pred_data['expected_home_goals']
                    existing_pred.expected_away_goals = pred_data['expected_away_goals']
                    existing_pred.model_version = "1.2.0-xg"
                    existing_pred.created_at = datetime.utcnow()
                    predictions_updated += 1
                else:
                    # Create new
                    prediction = Prediction(
                        fixture_id=fixture.id,
                        model_version="1.2.0-xg",
                        prob_home_win=pred_data['prob_home_win'],
                        prob_draw=pred_data['prob_draw'],
                        prob_away_win=pred_data['prob_away_win'],
                        prob_over_25=pred_data['prob_over_25'],
                        prob_under_25=pred_data['prob_under_25'],
                        prob_btts_yes=pred_data['prob_btts_yes'],
                        prob_btts_no=pred_data['prob_btts_no'],
                        most_likely_score=pred_data['most_likely_score'],
                        confidence_score=confidence,
                        expected_home_goals=pred_data['expected_home_goals'],
                        expected_away_goals=pred_data['expected_away_goals']
                    )
                    session.add(prediction)
                    predictions_created += 1
                    
            except ValueError as e:
                logger.warning(f"Skipping {fixture.home_team.name} vs {fixture.away_team.name}: {e}")
                continue
                
        await session.commit()
        logger.info(f"✅ Seeding complete: {predictions_created} created, {predictions_updated} updated.")

if __name__ == "__main__":
    asyncio.run(seed_predictions())
