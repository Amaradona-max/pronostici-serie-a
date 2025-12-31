"""
Script to seed realistic predictions for all fixtures
Populates predictions table with realistic data based on team strength
Run with: python -m app.scripts.seed_predictions
"""

import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy import select
import random

from app.db.engine import AsyncSessionLocal
from app.db.models import Fixture, Team, Prediction, TeamStats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_team_strength(stats):
    """Calculate team strength based on stats (0-100)"""
    if not stats:
        return 50.0

    # Weighted average of multiple factors
    points_per_game = (stats.wins * 3 + stats.draws) / max(stats.matches_played, 1) * 10
    goal_diff = (stats.goals_scored - stats.goals_conceded) / max(stats.matches_played, 1) * 10
    win_rate = (stats.wins / max(stats.matches_played, 1)) * 50

    strength = (points_per_game * 0.4) + (goal_diff * 0.3) + (win_rate * 0.3)
    return max(0, min(100, strength))


def generate_prediction(home_strength, away_strength, is_home_advantage=True):
    """
    Generate realistic prediction probabilities based on team strengths
    Uses ELO-like approach with home advantage
    """
    # Home advantage factor (historically 3-5 points)
    home_bonus = 4.0 if is_home_advantage else 0
    adjusted_home = home_strength + home_bonus

    # Calculate raw probabilities using logistic function
    strength_diff = adjusted_home - away_strength

    # Base probabilities (calibrated to real Serie A stats)
    if strength_diff > 20:
        prob_home = 0.55 + random.uniform(0, 0.15)
        prob_draw = 0.25 + random.uniform(-0.05, 0.05)
    elif strength_diff > 10:
        prob_home = 0.45 + random.uniform(0, 0.10)
        prob_draw = 0.28 + random.uniform(-0.05, 0.05)
    elif strength_diff > -10:
        prob_home = 0.35 + random.uniform(-0.05, 0.10)
        prob_draw = 0.30 + random.uniform(-0.05, 0.05)
    elif strength_diff > -20:
        prob_home = 0.25 + random.uniform(-0.05, 0.05)
        prob_draw = 0.28 + random.uniform(-0.05, 0.05)
    else:
        prob_home = 0.20 + random.uniform(-0.05, 0.05)
        prob_draw = 0.25 + random.uniform(-0.05, 0.05)

    prob_away = 1.0 - prob_home - prob_draw

    # Ensure probabilities are valid
    total = prob_home + prob_draw + prob_away
    prob_home /= total
    prob_draw /= total
    prob_away /= total

    # Over/Under 2.5 (based on team offensive/defensive stats)
    avg_goals = (home_strength + away_strength) / 40
    prob_over = 0.45 + (avg_goals - 2.5) * 0.15 + random.uniform(-0.1, 0.1)
    prob_over = max(0.30, min(0.70, prob_over))
    prob_under = 1.0 - prob_over

    # BTTS (Both Teams To Score)
    offensive_avg = (home_strength + away_strength) / 2
    prob_btts_yes = 0.40 + (offensive_avg - 50) * 0.006 + random.uniform(-0.1, 0.1)
    prob_btts_yes = max(0.35, min(0.65, prob_btts_yes))
    prob_btts_no = 1.0 - prob_btts_yes

    # Most likely score (based on probabilities)
    if prob_home > prob_draw and prob_home > prob_away:
        scores = ["2-0", "2-1", "1-0", "3-1"]
    elif prob_away > prob_home and prob_away > prob_draw:
        scores = ["0-1", "0-2", "1-2", "0-3"]
    else:
        scores = ["1-1", "0-0", "2-2"]

    most_likely_score = random.choice(scores)

    # Confidence score (based on clarity of prediction) - scaled 0 to 1
    max_prob = max(prob_home, prob_draw, prob_away)
    confidence = (max_prob - 0.33) / 0.67  # 0 to 1 scale
    confidence = max(0.5, min(0.95, confidence + random.uniform(-0.05, 0.05)))

    # Expected goals
    expected_home = 1.0 + (home_strength / 50) + random.uniform(-0.3, 0.3)
    expected_away = 0.8 + (away_strength / 50) + random.uniform(-0.3, 0.3)

    return {
        "prob_home_win": round(prob_home, 3),
        "prob_draw": round(prob_draw, 3),
        "prob_away_win": round(prob_away, 3),
        "prob_over_25": round(prob_over, 3),
        "prob_under_25": round(prob_under, 3),
        "prob_btts_yes": round(prob_btts_yes, 3),
        "prob_btts_no": round(prob_btts_no, 3),
        "most_likely_score": most_likely_score,
        "confidence_score": round(confidence, 1),
        "expected_home_goals": round(expected_home, 2),
        "expected_away_goals": round(expected_away, 2),
    }


async def seed_predictions():
    """Generate predictions for all fixtures"""
    async with AsyncSessionLocal() as session:
        logger.info("Starting predictions seeding...")

        # Get all fixtures with teams loaded
        from sqlalchemy.orm import selectinload
        fixtures_stmt = select(Fixture).options(
            selectinload(Fixture.home_team),
            selectinload(Fixture.away_team)
        ).order_by(Fixture.match_date)
        fixtures_result = await session.execute(fixtures_stmt)
        fixtures = fixtures_result.scalars().all()

        if not fixtures:
            logger.warning("No fixtures found in database")
            return

        # Get team stats
        stats_stmt = select(TeamStats).where(TeamStats.season == "2025-2026")
        stats_result = await session.execute(stats_stmt)
        team_stats = {stat.team_id: stat for stat in stats_result.scalars().all()}

        predictions_created = 0
        predictions_skipped = 0

        for fixture in fixtures:
            # Check if prediction already exists
            existing_stmt = select(Prediction).where(
                Prediction.fixture_id == fixture.id
            )
            existing = (await session.execute(existing_stmt)).scalar_one_or_none()

            if existing:
                predictions_skipped += 1
                continue

            # Get team strengths
            home_stats = team_stats.get(fixture.home_team_id)
            away_stats = team_stats.get(fixture.away_team_id)

            home_strength = calculate_team_strength(home_stats)
            away_strength = calculate_team_strength(away_stats)

            # Generate prediction
            pred_data = generate_prediction(home_strength, away_strength)

            # Calculate computation time (simulated)
            # Earlier predictions = older computation time
            hours_before_match = max(1, random.randint(24, 72))
            created_at = fixture.match_date - timedelta(hours=hours_before_match)

            # Create prediction
            prediction = Prediction(
                fixture_id=fixture.id,
                prob_home_win=pred_data["prob_home_win"],
                prob_draw=pred_data["prob_draw"],
                prob_away_win=pred_data["prob_away_win"],
                prob_over_25=pred_data["prob_over_25"],
                prob_under_25=pred_data["prob_under_25"],
                prob_btts_yes=pred_data["prob_btts_yes"],
                prob_btts_no=pred_data["prob_btts_no"],
                most_likely_score=pred_data["most_likely_score"],
                confidence_score=pred_data["confidence_score"],
                expected_home_goals=pred_data["expected_home_goals"],
                expected_away_goals=pred_data["expected_away_goals"],
                model_version="dixon-coles-v1.2.0",
                created_at=created_at
            )

            session.add(prediction)
            predictions_created += 1

            logger.info(
                f"Created prediction for fixture {fixture.id}: "
                f"{fixture.home_team.name} vs {fixture.away_team.name} | "
                f"1X2: {pred_data['prob_home_win']:.0%}-{pred_data['prob_draw']:.0%}-{pred_data['prob_away_win']:.0%} | "
                f"Score: {pred_data['most_likely_score']} | "
                f"Confidence: {pred_data['confidence_score']:.1f}%"
            )

        await session.commit()
        logger.info(
            f"✅ Predictions seeding completed! "
            f"Created: {predictions_created}, Skipped: {predictions_skipped}"
        )
        logger.info(f"🗓️  Saved at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(seed_predictions())
