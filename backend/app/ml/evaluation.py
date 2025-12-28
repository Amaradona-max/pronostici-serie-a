"""
Prediction Evaluation Module
Metrics for assessing prediction model performance
"""

import numpy as np
from sklearn.metrics import log_loss, brier_score_loss
from sklearn.calibration import calibration_curve
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class PredictionEvaluator:
    """
    Evaluates prediction model performance using standard metrics.

    Metrics:
    - Accuracy: Simple correctness rate
    - Log Loss: Penalizes confident wrong predictions
    - Brier Score: Mean squared error of probabilities
    - Expected Calibration Error (ECE): Calibration quality
    """

    def evaluate_1x2(
        self,
        y_true: np.ndarray,
        y_pred_proba: np.ndarray
    ) -> Dict[str, float]:
        """
        Evaluate 1X2 predictions.

        Args:
            y_true: True outcomes (0=home, 1=draw, 2=away)
            y_pred_proba: Predicted probabilities [P(home), P(draw), P(away)]

        Returns:
            Dictionary with metrics
        """
        if len(y_true) == 0:
            logger.warning("No predictions to evaluate")
            return {
                'accuracy': 0.0,
                'log_loss': 0.0,
                'brier_score': 0.0,
                'expected_calibration_error': 0.0
            }

        # Accuracy
        y_pred_class = y_pred_proba.argmax(axis=1)
        accuracy = (y_pred_class == y_true).mean()

        # Log Loss (lower is better, 0 = perfect)
        try:
            log_loss_val = log_loss(y_true, y_pred_proba)
        except Exception as e:
            logger.error(f"Error calculating log loss: {e}")
            log_loss_val = np.inf

        # Brier Score (multi-class)
        y_true_onehot = np.eye(3)[y_true]
        brier_score = np.mean((y_pred_proba - y_true_onehot) ** 2)

        # Expected Calibration Error
        ece = self._expected_calibration_error(y_true, y_pred_proba)

        return {
            'accuracy': float(accuracy),
            'log_loss': float(log_loss_val),
            'brier_score': float(brier_score),
            'expected_calibration_error': float(ece),
            'n_predictions': len(y_true)
        }

    def _expected_calibration_error(
        self,
        y_true: np.ndarray,
        y_pred_proba: np.ndarray,
        n_bins: int = 10
    ) -> float:
        """
        Calculate Expected Calibration Error (ECE).

        ECE measures how well predicted probabilities match observed frequencies.
        Lower is better, 0 = perfect calibration.

        Args:
            y_true: True class labels
            y_pred_proba: Predicted probabilities
            n_bins: Number of bins for calibration (default 10)

        Returns:
            ECE value
        """
        y_pred_class = y_pred_proba.argmax(axis=1)
        confidences = y_pred_proba.max(axis=1)
        accuracies = (y_pred_class == y_true).astype(float)

        ece = 0.0
        bin_boundaries = np.linspace(0, 1, n_bins + 1)

        for i in range(n_bins):
            bin_lower = bin_boundaries[i]
            bin_upper = bin_boundaries[i + 1]

            # Find predictions in this bin
            in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
            prop_in_bin = in_bin.mean()

            if prop_in_bin > 0:
                accuracy_in_bin = accuracies[in_bin].mean()
                avg_confidence_in_bin = confidences[in_bin].mean()

                # Weighted absolute difference
                ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin

        return ece

    def calculate_calibration_curve(
        self,
        y_true: np.ndarray,
        y_pred_proba: np.ndarray,
        n_bins: int = 10,
        outcome_class: int = 0
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate calibration curve for a specific outcome class.

        Args:
            y_true: True outcomes
            y_pred_proba: Predicted probabilities
            n_bins: Number of bins
            outcome_class: Which outcome to plot (0=home, 1=draw, 2=away)

        Returns:
            (prob_true, prob_pred) arrays for plotting
        """
        # Binary indicator for this outcome
        y_binary = (y_true == outcome_class).astype(int)
        y_prob = y_pred_proba[:, outcome_class]

        prob_true, prob_pred = calibration_curve(
            y_binary,
            y_prob,
            n_bins=n_bins,
            strategy='uniform'
        )

        return prob_true, prob_pred

    def evaluate_binary(
        self,
        y_true: np.ndarray,
        y_pred_proba: np.ndarray
    ) -> Dict[str, float]:
        """
        Evaluate binary predictions (e.g., Over/Under, BTTS).

        Args:
            y_true: True outcomes (0 or 1)
            y_pred_proba: Predicted probabilities

        Returns:
            Dictionary with metrics
        """
        if len(y_true) == 0:
            return {
                'accuracy': 0.0,
                'log_loss': 0.0,
                'brier_score': 0.0,
                'n_predictions': 0
            }

        # Accuracy
        y_pred_class = (y_pred_proba > 0.5).astype(int)
        accuracy = (y_pred_class == y_true).mean()

        # Log Loss
        try:
            log_loss_val = log_loss(y_true, y_pred_proba)
        except Exception as e:
            logger.error(f"Error calculating binary log loss: {e}")
            log_loss_val = np.inf

        # Brier Score
        try:
            brier = brier_score_loss(y_true, y_pred_proba)
        except Exception as e:
            logger.error(f"Error calculating Brier score: {e}")
            brier = np.inf

        return {
            'accuracy': float(accuracy),
            'log_loss': float(log_loss_val),
            'brier_score': float(brier),
            'n_predictions': len(y_true)
        }

    def performance_breakdown(
        self,
        y_true: np.ndarray,
        y_pred_proba: np.ndarray
    ) -> Dict[str, Dict]:
        """
        Performance breakdown by outcome type.

        Args:
            y_true: True outcomes (0=home, 1=draw, 2=away)
            y_pred_proba: Predicted probabilities

        Returns:
            Dictionary with per-outcome metrics
        """
        outcome_names = ['home_win', 'draw', 'away_win']
        breakdown = {}

        for idx, name in enumerate(outcome_names):
            # Predictions for this outcome
            mask = y_true == idx
            if mask.sum() == 0:
                continue

            y_pred_class = y_pred_proba.argmax(axis=1)

            # Precision: Of predictions for this outcome, how many were correct?
            predicted_as_this = y_pred_class == idx
            if predicted_as_this.sum() > 0:
                precision = (
                    (predicted_as_this & mask).sum() / predicted_as_this.sum()
                )
            else:
                precision = 0.0

            # Recall: Of actual occurrences, how many did we predict?
            recall = (predicted_as_this & mask).sum() / mask.sum()

            # F1 Score
            if precision + recall > 0:
                f1 = 2 * (precision * recall) / (precision + recall)
            else:
                f1 = 0.0

            breakdown[name] = {
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1),
                'occurrences': int(mask.sum())
            }

        return breakdown
