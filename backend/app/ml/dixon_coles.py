"""
Dixon-Coles Model Implementation
Statistical model for football match prediction

Paper: "Modelling Association Football Scores and Inefficiencies in the Football Betting Market"
Authors: Mark J. Dixon and Stuart G. Coles (1997)

This is an open-source implementation using numpy and scipy.
"""

import numpy as np
from scipy.optimize import minimize
from scipy.stats import poisson
from typing import Tuple, Dict, List
import logging
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)


class DixonColesModel:
    """
    Dixon-Coles model for football predictions.

    Models match outcomes using bivariate Poisson distribution with:
    - Home advantage parameter
    - Attack and defense strengths for each team
    - Dependency correction for low scores (0-0, 1-0, 0-1, 1-1)
    - Optional time decay for weighting recent matches
    """

    def __init__(
        self,
        home_advantage: float = 1.3,
        rho: float = 0.03,
        xi: float = 0.0018
    ):
        """
        Initialize Dixon-Coles model.

        Args:
            home_advantage: Home advantage multiplier (default 1.3 for Serie A)
            rho: Dependency parameter for low scores (default 0.03)
            xi: Time decay parameter (default 0.0018)
        """
        self.home_advantage = home_advantage
        self.rho = rho
        self.xi = xi

        self.attack_params: Dict[str, float] = {}
        self.defense_params: Dict[str, float] = {}
        self.team_list: List[str] = []

        self._is_fitted = False

    def tau(self, x: int, y: int, lambda_: float, mu: float) -> float:
        """
        Dependency function τ(x,y) for low score correction.

        Adjusts probabilities for 0-0, 1-0, 0-1, 1-1 scores based on
        empirical observation that these occur more/less frequently than
        independent Poisson would predict.

        Args:
            x: Home team goals
            y: Away team goals
            lambda_: Expected home goals (λ)
            mu: Expected away goals (μ)

        Returns:
            Correction factor
        """
        if x == 0 and y == 0:
            return 1 - lambda_ * mu * self.rho
        elif x == 0 and y == 1:
            return 1 + lambda_ * self.rho
        elif x == 1 and y == 0:
            return 1 + mu * self.rho
        elif x == 1 and y == 1:
            return 1 - self.rho
        else:
            return 1.0

    def predict_scoreline_probabilities(
        self,
        lambda_: float,
        mu: float,
        max_goals: int = 10
    ) -> np.ndarray:
        """
        Calculate probability matrix for all scorelines.

        Args:
            lambda_: Expected home goals
            mu: Expected away goals
            max_goals: Maximum goals to calculate (default 10)

        Returns:
            (max_goals+1, max_goals+1) array of probabilities
        """
        prob_matrix = np.zeros((max_goals + 1, max_goals + 1))

        for i in range(max_goals + 1):
            for j in range(max_goals + 1):
                # Independent Poisson probabilities
                poisson_prob = poisson.pmf(i, lambda_) * poisson.pmf(j, mu)

                # Dixon-Coles correction
                tau_correction = self.tau(i, j, lambda_, mu)

                prob_matrix[i, j] = poisson_prob * tau_correction

        # Normalize to ensure sum = 1.0
        prob_matrix /= prob_matrix.sum()

        return prob_matrix

    def predict_match(
        self,
        home_team: str,
        away_team: str,
        home_form_factor: float = 1.0,
        away_form_factor: float = 1.0
    ) -> Dict:
        """
        Predict probabilities for a match.

        Args:
            home_team: Home team name
            away_team: Away team name
            home_form_factor: Multiplier for home form (default 1.0)
            away_form_factor: Multiplier for away form (default 1.0)

        Returns:
            Dictionary with predictions:
            - prob_home_win, prob_draw, prob_away_win
            - prob_over_25, prob_under_25
            - prob_btts_yes, prob_btts_no
            - expected_home_goals, expected_away_goals
            - most_likely_score
        """
        if not self._is_fitted:
            raise ValueError("Model must be fitted before making predictions")

        if home_team not in self.attack_params or away_team not in self.attack_params:
            raise ValueError(f"Team not found in fitted model")

        # Get team parameters
        alpha_home = self.attack_params[home_team]
        beta_home = self.defense_params[home_team]
        alpha_away = self.attack_params[away_team]
        beta_away = self.defense_params[away_team]

        # Calculate expected goals
        lambda_ = (
            alpha_home * beta_away * self.home_advantage * home_form_factor
        )
        mu = (
            alpha_away * beta_home * (1 / self.home_advantage) * away_form_factor
        )

        # Get scoreline probability matrix
        prob_matrix = self.predict_scoreline_probabilities(lambda_, mu, max_goals=10)

        # Calculate 1X2 probabilities
        prob_home_win = np.tril(prob_matrix, -1).sum()  # i > j
        prob_draw = np.diag(prob_matrix).sum()  # i == j
        prob_away_win = np.triu(prob_matrix, 1).sum()  # i < j

        # Over/Under 2.5
        prob_over_25 = sum(
            prob_matrix[i, j]
            for i in range(11)
            for j in range(11)
            if i + j > 2.5
        )
        prob_under_25 = 1.0 - prob_over_25

        # Both Teams To Score (BTTS)
        prob_btts_no = (
            prob_matrix[0, :].sum() +  # Home team 0 goals
            prob_matrix[:, 0].sum() -  # Away team 0 goals
            prob_matrix[0, 0]          # Avoid double counting 0-0
        )
        prob_btts_yes = 1.0 - prob_btts_no

        # Most likely scoreline
        most_likely_idx = np.unravel_index(
            prob_matrix.argmax(),
            prob_matrix.shape
        )
        most_likely_score = f"{most_likely_idx[0]}-{most_likely_idx[1]}"
        most_likely_score_prob = prob_matrix[most_likely_idx]

        return {
            'prob_home_win': float(prob_home_win),
            'prob_draw': float(prob_draw),
            'prob_away_win': float(prob_away_win),
            'prob_over_25': float(prob_over_25),
            'prob_under_25': float(prob_under_25),
            'prob_btts_yes': float(prob_btts_yes),
            'prob_btts_no': float(prob_btts_no),
            'expected_home_goals': float(lambda_),
            'expected_away_goals': float(mu),
            'most_likely_score': most_likely_score,
            'most_likely_score_prob': float(most_likely_score_prob),
            'scoreline_probs': prob_matrix
        }

    def fit(
        self,
        matches: List[Dict],
        time_decay: bool = True
    ):
        """
        Fit the Dixon-Coles model to historical match data.

        Args:
            matches: List of match dictionaries with keys:
                - home_team: str
                - away_team: str
                - home_score: int
                - away_score: int
                - date: datetime (optional, for time decay)
            time_decay: Whether to apply time decay weighting

        Returns:
            Optimization result
        """
        if not matches:
            raise ValueError("No matches provided for fitting")

        logger.info(f"Fitting Dixon-Coles model on {len(matches)} matches")

        # Get unique teams
        teams = set()
        for match in matches:
            teams.add(match['home_team'])
            teams.add(match['away_team'])

        self.team_list = sorted(teams)
        n_teams = len(self.team_list)
        team_to_idx = {team: i for i, team in enumerate(self.team_list)}

        logger.info(f"Found {n_teams} unique teams")

        # Calculate time weights if applicable
        weights = []
        if time_decay and 'date' in matches[0]:
            max_date = max(m['date'] for m in matches)
            for match in matches:
                days_ago = (max_date - match['date']).days
                weight = np.exp(-self.xi * days_ago)
                weights.append(weight)
        else:
            weights = [1.0] * len(matches)

        # Define negative log-likelihood function
        def negative_log_likelihood(params):
            """Objective function to minimize"""

            # Unpack parameters
            attack = params[:n_teams]
            defense = params[n_teams:2 * n_teams]
            home_adv = params[-2]
            rho = params[-1]

            # Ensure all parameters are positive
            if np.any(attack <= 0) or np.any(defense <= 0) or home_adv <= 0:
                return 1e10  # Return large penalty

            log_likelihood = 0.0

            for idx, match in enumerate(matches):
                i = team_to_idx[match['home_team']]
                j = team_to_idx[match['away_team']]

                # Expected goals
                lambda_ = attack[i] * defense[j] * home_adv
                mu = attack[j] * defense[i]

                x = match['home_score']
                y = match['away_score']

                # Poisson probability with tau correction
                poisson_prob = (
                    poisson.pmf(x, lambda_) * poisson.pmf(y, mu)
                )
                tau_val = self.tau(x, y, lambda_, mu)

                prob = poisson_prob * tau_val

                # Weighted log likelihood
                if prob > 0:
                    log_likelihood += weights[idx] * np.log(prob)
                else:
                    log_likelihood -= 1e6  # Penalty for zero probability

            return -log_likelihood

        # Initial parameters
        init_attack = np.ones(n_teams)
        init_defense = np.ones(n_teams)
        init_home_adv = 1.3
        init_rho = 0.03

        x0 = np.concatenate([init_attack, init_defense, [init_home_adv, init_rho]])

        # Bounds
        bounds = (
            [(0.1, 5.0)] * (2 * n_teams) +  # attack, defense
            [(1.0, 2.0)] +                   # home advantage
            [(-0.5, 0.5)]                    # rho
        )

        # Optimize
        logger.info("Starting optimization...")
        result = minimize(
            negative_log_likelihood,
            x0,
            method='L-BFGS-B',
            bounds=bounds,
            options={'maxiter': 1000}
        )

        if not result.success:
            logger.warning(f"Optimization did not converge: {result.message}")

        # Extract fitted parameters
        optimal_params = result.x
        for idx, team in enumerate(self.team_list):
            self.attack_params[team] = optimal_params[idx]
            self.defense_params[team] = optimal_params[n_teams + idx]

        self.home_advantage = optimal_params[-2]
        self.rho = optimal_params[-1]

        self._is_fitted = True

        logger.info(
            f"Model fitted successfully. Home advantage: {self.home_advantage:.3f}, "
            f"rho: {self.rho:.4f}"
        )

        return result

    def fit_xg(
        self,
        matches: List[Dict],
        time_decay: bool = True
    ):
        """
        Fit model using Expected Goals (xG) instead of actual goals.
        Minimizes Mean Squared Error between predicted lambda/mu and actual xG.
        
        This is often more accurate as xG is less noisy than goals.
        """
        if not matches:
            raise ValueError("No matches provided for fitting")

        logger.info(f"Fitting Dixon-Coles model on {len(matches)} matches using xG")

        # Get unique teams
        teams = set()
        for match in matches:
            teams.add(match['home_team'])
            teams.add(match['away_team'])

        self.team_list = sorted(teams)
        n_teams = len(self.team_list)
        team_to_idx = {team: i for i, team in enumerate(self.team_list)}

        # Weights
        weights = []
        if time_decay and 'date' in matches[0]:
            max_date = max(m['date'] for m in matches)
            for match in matches:
                days_ago = (max_date - match['date']).days
                weight = np.exp(-self.xi * days_ago)
                weights.append(weight)
        else:
            weights = [1.0] * len(matches)

        def loss_function(params):
            # Unpack parameters
            attack = params[:n_teams]
            defense = params[n_teams:2 * n_teams]
            home_adv = params[-1]  # No rho for xG fitting

            if np.any(attack <= 0) or np.any(defense <= 0) or home_adv <= 0:
                return 1e10

            loss = 0.0
            
            # Constraint: Avg Attack = 1.0 (to fix scale)
            # We add this as a penalty
            scale_penalty = (np.mean(attack) - 1.0)**2 + (np.mean(defense) - 1.0)**2

            for idx, match in enumerate(matches):
                i = team_to_idx[match['home_team']]
                j = team_to_idx[match['away_team']]

                # Predicted xG
                pred_home_xg = attack[i] * defense[j] * home_adv
                pred_away_xg = attack[j] * defense[i] # No home adv for away

                # Actual xG
                actual_home_xg = match.get('home_xg', match['home_score']) # Fallback to goals if xG missing
                actual_away_xg = match.get('away_xg', match['away_score'])

                # Weighted Squared Error
                error = (pred_home_xg - actual_home_xg)**2 + (pred_away_xg - actual_away_xg)**2
                loss += weights[idx] * error

            return loss + (scale_penalty * 1000)

        # Initial parameters
        x0 = np.concatenate([
            np.ones(n_teams),          # Attack
            np.ones(n_teams),          # Defense
            [1.2]                      # Home Adv
        ])

        # Bounds
        bounds = (
            [(0.1, 5.0)] * (2 * n_teams) +
            [(0.8, 1.6)]  # Home Adv
        )

        result = minimize(
            loss_function,
            x0,
            method='L-BFGS-B',
            bounds=bounds
        )

        # Extract parameters
        optimal_params = result.x
        for idx, team in enumerate(self.team_list):
            self.attack_params[team] = optimal_params[idx]
            self.defense_params[team] = optimal_params[n_teams + idx]

        self.home_advantage = optimal_params[-1]
        self.rho = 0.0 # xG fitting doesn't estimate rho, assume independent

        self._is_fitted = True
        logger.info(f"Model fitted with xG. Home Adv: {self.home_advantage:.3f}")
        
        return result

    def save(self, filepath: str):
        """Save model to disk"""
        model_data = {
            'attack_params': self.attack_params,
            'defense_params': self.defense_params,
            'home_advantage': self.home_advantage,
            'rho': self.rho,
            'xi': self.xi,
            'team_list': self.team_list,
            'is_fitted': self._is_fitted
        }

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)

        logger.info(f"Model saved to {filepath}")

    @classmethod
    def load(cls, filepath: str) -> 'DixonColesModel':
        """Load model from disk"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)

        model = cls(
            home_advantage=model_data['home_advantage'],
            rho=model_data['rho'],
            xi=model_data['xi']
        )

        model.attack_params = model_data['attack_params']
        model.defense_params = model_data['defense_params']
        model.team_list = model_data['team_list']
        model._is_fitted = model_data['is_fitted']

        logger.info(f"Model loaded from {filepath}")

        return model
