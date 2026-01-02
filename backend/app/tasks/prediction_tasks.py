"""
Celery Tasks for Prediction Generation and Evaluation
"""

from celery import shared_task
from sqlalchemy import select, and_
from datetime import datetime, timedelta
import logging
import asyncio
import numpy as np

from app.tasks.celery_app import celery_app
from app.db import models
from app.db.engine import AsyncSessionLocal
from app.ml.dixon_coles import DixonColesModel
from app.ml.evaluation import PredictionEvaluator
from app.services.feature_extraction import FeatureExtractor
from app.config import get_settings
import os

logger = logging.getLogger(__name__)
settings = get_settings()

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "saved_models", "dixon_coles_latest.pkl")


def run_async(coroutine):
    """Helper to run async functions in Celery tasks"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coroutine)


@shared_task(bind=True, max_retries=3)
def generate_predictions(self, fixture_id: int, force_regenerate: bool = False):
    """
    Generate ML predictions for a specific fixture.

    Args:
        fixture_id: Database ID of the fixture
        force_regenerate: If True, regenerate even if prediction exists
    """
    try:
        logger.info(f"Generating predictions for fixture {fixture_id}")

        async def _generate():
            async with AsyncSessionLocal() as session:
                # Get fixture with relationships
                stmt = select(models.Fixture).where(
                    models.Fixture.id == fixture_id
                )
                fixture = (await session.execute(stmt)).scalar_one_or_none()

                if not fixture:
                    logger.error(f"Fixture {fixture_id} not found")
                    return

                # Check if prediction already exists
                pred_stmt = select(models.Prediction).where(
                    and_(
                        models.Prediction.fixture_id == fixture_id,
                        models.Prediction.model_version == '1.0'  # TODO: Get from config
                    )
                ).order_by(models.Prediction.created_at.desc())

                existing_pred = (await session.execute(pred_stmt)).scalar_one_or_none()

                if existing_pred and not force_regenerate:
                    logger.info(f"Prediction already exists for fixture {fixture_id}")
                    return

                # Extract features
                feature_extractor = FeatureExtractor(session)
                features = await feature_extractor.extract_features(fixture_id)

                # Load ML model
                model = DixonColesModel()
                if os.path.exists(MODEL_PATH):
                    try:
                        model = DixonColesModel.load(MODEL_PATH)
                        logger.info(f"Loaded trained model from {MODEL_PATH}")
                    except Exception as e:
                        logger.error(f"Failed to load model: {e}")
                
                # Check if model is fitted
                if not model._is_fitted:
                    logger.warning("Model not fitted and no saved model found. Skipping prediction.")
                    return

                # Generate prediction
                home_form_factor = features.get('home_form_factor', 1.0)
                away_form_factor = features.get('away_form_factor', 1.0)

                # Safe prediction (handle new teams)
                try:
                    prediction = model.predict_match(
                        fixture.home_team.name,
                        fixture.away_team.name,
                        home_form_factor=home_form_factor,
                        away_form_factor=away_form_factor
                    )
                except ValueError as e:
                    logger.warning(f"Could not predict fixture {fixture_id}: {e}")
                    # Fallback or skip
                    return

                # Save prediction to database
                new_prediction = models.Prediction(
                    fixture_id=fixture_id,
                    model_version='1.2.0-xg',
                    prob_home_win=prediction['prob_home_win'],
                    prob_draw=prediction['prob_draw'],
                    prob_away_win=prediction['prob_away_win'],
                    prob_over_25=prediction['prob_over_25'],
                    prob_under_25=prediction['prob_under_25'],
                    prob_btts_yes=prediction['prob_btts_yes'],
                    prob_btts_no=prediction['prob_btts_no'],
                    expected_home_goals=prediction['expected_home_goals'],
                    expected_away_goals=prediction['expected_away_goals'],
                    most_likely_score=prediction['most_likely_score'],
                    confidence_score=max(
                        prediction['prob_home_win'],
                        prediction['prob_draw'],
                        prediction['prob_away_win']
                    ),
                    created_at=datetime.utcnow()
                )

                session.add(new_prediction)

                # Save feature snapshot for audit trail
                feature_snapshot = models.FeatureSnapshot(
                    prediction=new_prediction,
                    home_elo_rating=features.get('home_elo', 1500),
                    away_elo_rating=features.get('away_elo', 1500),
                    home_form_last5=features.get('home_form_last5', 0),
                    away_form_last5=features.get('away_form_last5', 0),
                    home_goals_scored_avg=features.get('home_goals_scored_avg', 0),
                    away_goals_scored_avg=features.get('away_goals_scored_avg', 0),
                    home_goals_conceded_avg=features.get('home_goals_conceded_avg', 0),
                    away_goals_conceded_avg=features.get('away_goals_conceded_avg', 0),
                    home_injuries_count=features.get('home_injuries_count', 0),
                    away_injuries_count=features.get('away_injuries_count', 0),
                    h2h_home_wins=features.get('h2h_home_wins', 0),
                    h2h_draws=features.get('h2h_draws', 0),
                    h2h_away_wins=features.get('h2h_away_wins', 0),
                    snapshot_timestamp=datetime.utcnow()
                )

                session.add(feature_snapshot)
                await session.commit()

                logger.info(
                    f"✅ Prediction saved for fixture {fixture_id}: "
                    f"Home {prediction['prob_home_win']:.2%}, "
                    f"Draw {prediction['prob_draw']:.2%}, "
                    f"Away {prediction['prob_away_win']:.2%}"
                )

        run_async(_generate())

    except Exception as exc:
        logger.error(f"Error generating prediction for fixture {fixture_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def evaluate_finished_matches():
    """
    PERIODIC TASK: Evaluate predictions for recently finished matches.

    This task:
    1. Finds matches that finished in the last 6 hours
    2. Compares predictions against actual results
    3. Calculates accuracy metrics
    4. Stores evaluation results
    """
    try:
        logger.info("Starting evaluation of finished matches")

        async def _evaluate():
            async with AsyncSessionLocal() as session:
                # Find fixtures that finished in the last 6 hours
                cutoff_time = datetime.utcnow() - timedelta(hours=6)

                stmt = select(models.Fixture).where(
                    and_(
                        models.Fixture.status == 'finished',
                        models.Fixture.match_date >= cutoff_time,
                        models.Fixture.home_score.isnot(None),
                        models.Fixture.away_score.isnot(None)
                    )
                )

                finished_fixtures = (await session.execute(stmt)).scalars().all()

                if not finished_fixtures:
                    logger.info("No recently finished matches to evaluate")
                    return

                logger.info(f"Evaluating {len(finished_fixtures)} finished matches")

                evaluator = PredictionEvaluator()
                evaluated_count = 0

                for fixture in finished_fixtures:
                    try:
                        # Get the most recent prediction for this fixture
                        pred_stmt = select(models.Prediction).where(
                            models.Prediction.fixture_id == fixture.id
                        ).order_by(models.Prediction.created_at.desc())

                        prediction = (await session.execute(pred_stmt)).scalar_one_or_none()

                        if not prediction:
                            logger.warning(f"No prediction found for fixture {fixture.id}")
                            continue

                        # Check if already evaluated
                        eval_stmt = select(models.PredictionEvaluation).where(
                            models.PredictionEvaluation.prediction_id == prediction.id
                        )

                        existing_eval = (await session.execute(eval_stmt)).scalar_one_or_none()

                        if existing_eval:
                            logger.info(f"Fixture {fixture.id} already evaluated")
                            continue

                        # Determine actual outcome
                        if fixture.home_score > fixture.away_score:
                            actual_outcome_1x2 = 'home'
                            actual_outcome_idx = 0
                        elif fixture.home_score < fixture.away_score:
                            actual_outcome_1x2 = 'away'
                            actual_outcome_idx = 2
                        else:
                            actual_outcome_1x2 = 'draw'
                            actual_outcome_idx = 1

                        # Predicted outcome
                        probs = [
                            prediction.prob_home_win,
                            prediction.prob_draw,
                            prediction.prob_away_win
                        ]
                        predicted_outcome_idx = np.argmax(probs)
                        outcome_map = {0: 'home', 1: 'draw', 2: 'away'}
                        predicted_outcome_1x2 = outcome_map[predicted_outcome_idx]

                        # Check if prediction was correct
                        is_correct_1x2 = (actual_outcome_1x2 == predicted_outcome_1x2)

                        # Over/Under 2.5
                        total_goals = fixture.home_score + fixture.away_score
                        actual_over_25 = total_goals > 2.5
                        predicted_over_25 = prediction.prob_over_25 > 0.5
                        is_correct_over_under = (actual_over_25 == predicted_over_25)

                        # BTTS (Both Teams To Score)
                        actual_btts = (fixture.home_score > 0 and fixture.away_score > 0)
                        predicted_btts = prediction.prob_btts_yes > 0.5
                        is_correct_btts = (actual_btts == predicted_btts)

                        # Calculate Brier scores
                        y_true_onehot = np.eye(3)[actual_outcome_idx]
                        y_pred = np.array(probs)
                        brier_score_1x2 = float(np.mean((y_pred - y_true_onehot) ** 2))

                        # Brier for Over/Under
                        brier_over_under = (prediction.prob_over_25 - float(actual_over_25)) ** 2

                        # Brier for BTTS
                        brier_btts = (prediction.prob_btts_yes - float(actual_btts)) ** 2

                        # Create evaluation record
                        evaluation = models.PredictionEvaluation(
                            prediction_id=prediction.id,
                            actual_outcome_1x2=actual_outcome_1x2,
                            predicted_outcome_1x2=predicted_outcome_1x2,
                            is_correct_1x2=is_correct_1x2,
                            is_correct_over_under=is_correct_over_under,
                            is_correct_btts=is_correct_btts,
                            brier_score_1x2=brier_score_1x2,
                            brier_score_over_under=brier_over_under,
                            brier_score_btts=brier_btts,
                            evaluated_at=datetime.utcnow()
                        )

                        session.add(evaluation)
                        evaluated_count += 1

                        result_emoji = "✅" if is_correct_1x2 else "❌"
                        logger.info(
                            f"{result_emoji} Fixture {fixture.id} evaluated: "
                            f"Predicted {predicted_outcome_1x2}, "
                            f"Actual {actual_outcome_1x2}, "
                            f"Brier: {brier_score_1x2:.4f}"
                        )

                    except Exception as e:
                        logger.error(f"Error evaluating fixture {fixture.id}: {str(e)}")
                        await session.rollback()
                        continue

                # Commit all evaluations
                await session.commit()

                logger.info(f"✅ Evaluated {evaluated_count} predictions successfully")

                # Calculate aggregate metrics for the period
                await _calculate_aggregate_metrics(session)

        run_async(_evaluate())

    except Exception as exc:
        logger.error(f"Error in evaluate_finished_matches: {str(exc)}")
        raise


async def _calculate_aggregate_metrics(session):
    """
    Calculate and log aggregate performance metrics.
    """
    try:
        # Get all evaluations from last 30 days
        cutoff = datetime.utcnow() - timedelta(days=30)

        stmt = select(models.PredictionEvaluation).where(
            models.PredictionEvaluation.evaluated_at >= cutoff
        )

        evaluations = (await session.execute(stmt)).scalars().all()

        if not evaluations:
            return

        # Calculate metrics
        total = len(evaluations)
        correct_1x2 = sum(1 for e in evaluations if e.is_correct_1x2)
        correct_over_under = sum(1 for e in evaluations if e.is_correct_over_under)
        correct_btts = sum(1 for e in evaluations if e.is_correct_btts)

        accuracy_1x2 = correct_1x2 / total
        accuracy_over_under = correct_over_under / total
        accuracy_btts = correct_btts / total

        avg_brier_1x2 = np.mean([e.brier_score_1x2 for e in evaluations])
        avg_brier_over_under = np.mean([e.brier_score_over_under for e in evaluations])
        avg_brier_btts = np.mean([e.brier_score_btts for e in evaluations])

        logger.info("=" * 50)
        logger.info("📊 PERFORMANCE METRICS (Last 30 days)")
        logger.info("=" * 50)
        logger.info(f"Total predictions evaluated: {total}")
        logger.info(f"1X2 Accuracy: {accuracy_1x2:.2%}")
        logger.info(f"Over/Under Accuracy: {accuracy_over_under:.2%}")
        logger.info(f"BTTS Accuracy: {accuracy_btts:.2%}")
        logger.info(f"1X2 Brier Score: {avg_brier_1x2:.4f}")
        logger.info(f"Over/Under Brier: {avg_brier_over_under:.4f}")
        logger.info(f"BTTS Brier: {avg_brier_btts:.4f}")
        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"Error calculating aggregate metrics: {str(e)}")


@shared_task(bind=True)
def batch_generate_predictions(self, season: str = "2025-2026"):
    """
    Generate predictions for all upcoming fixtures in the next 7 days.

    Args:
        season: Season to process (default: 2025-2026)
    """
    try:
        logger.info(f"Generating predictions for upcoming fixtures in season {season}")

        async def _batch_generate():
            async with AsyncSessionLocal() as session:
                # Find fixtures in the next 7 days
                now = datetime.utcnow()
                week_from_now = now + timedelta(days=7)

                stmt = select(models.Fixture).where(
                    and_(
                        models.Fixture.season == season,
                        models.Fixture.match_date.between(now, week_from_now),
                        models.Fixture.status == 'scheduled'
                    )
                )

                fixtures = (await session.execute(stmt)).scalars().all()

                if not fixtures:
                    logger.info("No upcoming fixtures found")
                    return

                logger.info(f"Found {len(fixtures)} upcoming fixtures")

                # Queue individual prediction tasks
                for fixture in fixtures:
                    generate_predictions.delay(fixture.id)
                    logger.info(f"Queued prediction task for fixture {fixture.id}")

        run_async(_batch_generate())

    except Exception as exc:
        logger.error(f"Error in batch_generate_predictions: {str(exc)}")
        raise
