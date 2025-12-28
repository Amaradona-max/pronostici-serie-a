"""
Feature Extraction Service
Extracts features from database for ML prediction models
"""

import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np

from app.db.models import (
    Fixture, Team, TeamStats, Injury, Suspension,
    MatchStats, Stadium
)

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """
    Extracts features for prediction models.

    Features extracted:
    - Team strength (ELO rating)
    - Attack/Defense strength (goals scored/conceded)
    - Home advantage (stadium-specific)
    - Recent form (weighted last 5 matches)
    - Injuries/Suspensions severity
    - Head-to-head history
    - xG statistics (if available)
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def extract_features(self, fixture_id: int) -> Dict:
        """
        Extract all features for a given fixture.

        Args:
            fixture_id: Fixture ID to extract features for

        Returns:
            Dictionary of features
        """
        # Get fixture with relationships
        stmt = select(Fixture).where(Fixture.id == fixture_id)
        result = await self.session.execute(stmt)
        fixture = result.scalar_one_or_none()

        if not fixture:
            raise ValueError(f"Fixture {fixture_id} not found")

        features = {}

        # Team strength features
        features.update(await self._get_team_strength_features(fixture))

        # Home advantage
        features.update(await self._get_home_advantage_features(fixture))

        # Recent form
        features.update(await self._get_form_features(fixture))

        # Injuries and suspensions
        features.update(await self._get_injury_features(fixture))
        features.update(await self._get_suspension_features(fixture))

        # Head-to-head
        features.update(await self._get_h2h_features(fixture))

        # Advanced stats (xG if available)
        features.update(await self._get_advanced_stats_features(fixture))

        # Context features
        features.update(await self._get_context_features(fixture))

        # Calculate data completeness
        total_features = len(features)
        non_null_features = sum(1 for v in features.values() if v is not None and v != 0.0)
        features['data_completeness'] = non_null_features / total_features if total_features > 0 else 0.0

        features['timestamp'] = datetime.utcnow()

        logger.info(
            f"Extracted {len(features)} features for fixture {fixture_id}, "
            f"completeness: {features['data_completeness']:.2%}"
        )

        return features

    async def _get_team_strength_features(self, fixture: Fixture) -> Dict:
        """Extract team strength features (ELO, goals)"""

        # Get home team
        home_team_stmt = select(Team).where(Team.id == fixture.home_team_id)
        home_team = (await self.session.execute(home_team_stmt)).scalar_one()

        # Get away team
        away_team_stmt = select(Team).where(Team.id == fixture.away_team_id)
        away_team = (await self.session.execute(away_team_stmt)).scalar_one()

        # Get team stats for current season
        home_stats_stmt = select(TeamStats).where(
            and_(
                TeamStats.team_id == fixture.home_team_id,
                TeamStats.season == fixture.season
            )
        )
        home_stats = (await self.session.execute(home_stats_stmt)).scalar_one_or_none()

        away_stats_stmt = select(TeamStats).where(
            and_(
                TeamStats.team_id == fixture.away_team_id,
                TeamStats.season == fixture.season
            )
        )
        away_stats = (await self.session.execute(away_stats_stmt)).scalar_one_or_none()

        return {
            'home_elo': float(home_team.elo_rating),
            'away_elo': float(away_team.elo_rating),
            'elo_diff': float(home_team.elo_rating - away_team.elo_rating),

            'home_goals_scored_avg': (
                float(home_stats.goals_scored / home_stats.matches_played)
                if home_stats and home_stats.matches_played > 0 else 0.0
            ),
            'home_goals_conceded_avg': (
                float(home_stats.goals_conceded / home_stats.matches_played)
                if home_stats and home_stats.matches_played > 0 else 0.0
            ),
            'away_goals_scored_avg': (
                float(away_stats.goals_scored / away_stats.matches_played)
                if away_stats and away_stats.matches_played > 0 else 0.0
            ),
            'away_goals_conceded_avg': (
                float(away_stats.goals_conceded / away_stats.matches_played)
                if away_stats and away_stats.matches_played > 0 else 0.0
            ),
        }

    async def _get_home_advantage_features(self, fixture: Fixture) -> Dict:
        """Extract home advantage features"""

        if not fixture.stadium_id:
            return {
                'stadium_home_advantage': 1.0,
                'home_win_rate_home': 0.0,
                'away_win_rate_away': 0.0,
            }

        # Get stadium
        stadium_stmt = select(Stadium).where(Stadium.id == fixture.stadium_id)
        stadium = (await self.session.execute(stadium_stmt)).scalar_one_or_none()

        # Get home team performance at home
        home_fixtures_stmt = select(Fixture).where(
            and_(
                Fixture.home_team_id == fixture.home_team_id,
                Fixture.season == fixture.season,
                Fixture.status == 'finished',
                Fixture.id != fixture.id
            )
        ).limit(10)
        home_fixtures = (await self.session.execute(home_fixtures_stmt)).scalars().all()

        home_wins = sum(
            1 for f in home_fixtures
            if f.home_score is not None and f.away_score is not None and f.home_score > f.away_score
        )
        home_win_rate = home_wins / len(home_fixtures) if home_fixtures else 0.0

        # Get away team performance away
        away_fixtures_stmt = select(Fixture).where(
            and_(
                Fixture.away_team_id == fixture.away_team_id,
                Fixture.season == fixture.season,
                Fixture.status == 'finished',
                Fixture.id != fixture.id
            )
        ).limit(10)
        away_fixtures = (await self.session.execute(away_fixtures_stmt)).scalars().all()

        away_wins = sum(
            1 for f in away_fixtures
            if f.home_score is not None and f.away_score is not None and f.away_score > f.home_score
        )
        away_win_rate = away_wins / len(away_fixtures) if away_fixtures else 0.0

        return {
            'stadium_home_advantage': float(stadium.home_advantage_factor) if stadium else 1.0,
            'home_win_rate_home': home_win_rate,
            'away_win_rate_away': away_win_rate,
        }

    async def _get_form_features(self, fixture: Fixture) -> Dict:
        """Extract recent form features (last 5 matches)"""

        # Home team last 5 matches
        home_last5_stmt = select(Fixture).where(
            or_(
                Fixture.home_team_id == fixture.home_team_id,
                Fixture.away_team_id == fixture.home_team_id
            ),
            Fixture.status == 'finished',
            Fixture.match_date < fixture.match_date,
            Fixture.id != fixture.id
        ).order_by(desc(Fixture.match_date)).limit(5)

        home_last5 = (await self.session.execute(home_last5_stmt)).scalars().all()

        home_form_points = self._calculate_form_points(home_last5, fixture.home_team_id)

        # Away team last 5 matches
        away_last5_stmt = select(Fixture).where(
            or_(
                Fixture.home_team_id == fixture.away_team_id,
                Fixture.away_team_id == fixture.away_team_id
            ),
            Fixture.status == 'finished',
            Fixture.match_date < fixture.match_date,
            Fixture.id != fixture.id
        ).order_by(desc(Fixture.match_date)).limit(5)

        away_last5 = (await self.session.execute(away_last5_stmt)).scalars().all()

        away_form_points = self._calculate_form_points(away_last5, fixture.away_team_id)

        return {
            'home_form_points': home_form_points,
            'away_form_points': away_form_points,
            'form_diff': home_form_points - away_form_points,
        }

    def _calculate_form_points(self, fixtures: list, team_id: int) -> float:
        """Calculate weighted form points for a team"""
        if not fixtures:
            return 0.0

        total_points = 0.0
        total_weight = 0.0

        for i, match in enumerate(fixtures):
            # Exponential decay weight (recent matches more important)
            weight = np.exp(-0.2 * i)

            # Determine result
            is_home = match.home_team_id == team_id

            if is_home:
                goals_for = match.home_score or 0
                goals_against = match.away_score or 0
            else:
                goals_for = match.away_score or 0
                goals_against = match.home_score or 0

            # Points
            if goals_for > goals_against:
                points = 3
            elif goals_for == goals_against:
                points = 1
            else:
                points = 0

            total_points += points * weight
            total_weight += weight

        return total_points / total_weight if total_weight > 0 else 0.0

    async def _get_injury_features(self, fixture: Fixture) -> Dict:
        """Extract injury severity features"""

        # Home team injuries
        home_injuries_stmt = select(Injury).where(
            and_(
                Injury.team_id == fixture.home_team_id,
                Injury.status == 'active',
                or_(
                    Injury.expected_return_date.is_(None),
                    Injury.expected_return_date > fixture.match_date.date()
                )
            )
        )
        home_injuries = (await self.session.execute(home_injuries_stmt)).scalars().all()

        # Away team injuries
        away_injuries_stmt = select(Injury).where(
            and_(
                Injury.team_id == fixture.away_team_id,
                Injury.status == 'active',
                or_(
                    Injury.expected_return_date.is_(None),
                    Injury.expected_return_date > fixture.match_date.date()
                )
            )
        )
        away_injuries = (await self.session.execute(away_injuries_stmt)).scalars().all()

        severity_weights = {
            'minor': 5,
            'moderate': 15,
            'major': 30,
            'severe': 50
        }

        home_injury_score = sum(
            severity_weights.get(inj.severity, 0) for inj in home_injuries
        )
        away_injury_score = sum(
            severity_weights.get(inj.severity, 0) for inj in away_injuries
        )

        return {
            'home_injury_severity': min(home_injury_score, 100),  # Cap at 100
            'away_injury_severity': min(away_injury_score, 100),
            'home_injuries_count': len(home_injuries),
            'away_injuries_count': len(away_injuries),
        }

    async def _get_suspension_features(self, fixture: Fixture) -> Dict:
        """Extract suspension features"""

        # Home team suspensions
        home_suspensions_stmt = select(Suspension).where(
            and_(
                Suspension.team_id == fixture.home_team_id,
                Suspension.status == 'active',
                Suspension.matches_remaining > 0
            )
        )
        home_suspensions = (await self.session.execute(home_suspensions_stmt)).scalars().all()

        # Away team suspensions
        away_suspensions_stmt = select(Suspension).where(
            and_(
                Suspension.team_id == fixture.away_team_id,
                Suspension.status == 'active',
                Suspension.matches_remaining > 0
            )
        )
        away_suspensions = (await self.session.execute(away_suspensions_stmt)).scalars().all()

        return {
            'home_suspensions_count': len(home_suspensions),
            'away_suspensions_count': len(away_suspensions),
        }

    async def _get_h2h_features(self, fixture: Fixture) -> Dict:
        """Extract head-to-head features"""

        # Get last 10 H2H matches
        h2h_stmt = select(Fixture).where(
            or_(
                and_(
                    Fixture.home_team_id == fixture.home_team_id,
                    Fixture.away_team_id == fixture.away_team_id
                ),
                and_(
                    Fixture.home_team_id == fixture.away_team_id,
                    Fixture.away_team_id == fixture.home_team_id
                )
            ),
            Fixture.status == 'finished',
            Fixture.match_date < fixture.match_date
        ).order_by(desc(Fixture.match_date)).limit(10)

        h2h_matches = (await self.session.execute(h2h_stmt)).scalars().all()

        if not h2h_matches:
            return {
                'h2h_home_wins': 0,
                'h2h_draws': 0,
                'h2h_away_wins': 0,
                'h2h_avg_goals': 0.0,
            }

        home_wins = 0
        draws = 0
        away_wins = 0
        total_goals = 0

        for match in h2h_matches:
            if match.home_score is None or match.away_score is None:
                continue

            # Determine from perspective of current fixture's home team
            if match.home_team_id == fixture.home_team_id:
                if match.home_score > match.away_score:
                    home_wins += 1
                elif match.home_score == match.away_score:
                    draws += 1
                else:
                    away_wins += 1
            else:
                if match.away_score > match.home_score:
                    home_wins += 1
                elif match.home_score == match.away_score:
                    draws += 1
                else:
                    away_wins += 1

            total_goals += match.home_score + match.away_score

        return {
            'h2h_home_wins': home_wins,
            'h2h_draws': draws,
            'h2h_away_wins': away_wins,
            'h2h_avg_goals': total_goals / len(h2h_matches) if h2h_matches else 0.0,
        }

    async def _get_advanced_stats_features(self, fixture: Fixture) -> Dict:
        """Extract advanced statistics (xG) if available"""

        # Get home team xG stats
        home_stats_stmt = select(TeamStats).where(
            and_(
                TeamStats.team_id == fixture.home_team_id,
                TeamStats.season == fixture.season
            )
        )
        home_stats = (await self.session.execute(home_stats_stmt)).scalar_one_or_none()

        # Get away team xG stats
        away_stats_stmt = select(TeamStats).where(
            and_(
                TeamStats.team_id == fixture.away_team_id,
                TeamStats.season == fixture.season
            )
        )
        away_stats = (await self.session.execute(away_stats_stmt)).scalar_one_or_none()

        return {
            'home_xg_per_game': (
                float(home_stats.xg_for / home_stats.matches_played)
                if home_stats and home_stats.matches_played > 0 else 0.0
            ),
            'away_xg_per_game': (
                float(away_stats.xg_for / away_stats.matches_played)
                if away_stats and away_stats.matches_played > 0 else 0.0
            ),
            'home_xga_per_game': (
                float(home_stats.xg_against / home_stats.matches_played)
                if home_stats and home_stats.matches_played > 0 else 0.0
            ),
            'away_xga_per_game': (
                float(away_stats.xg_against / away_stats.matches_played)
                if away_stats and away_stats.matches_played > 0 else 0.0
            ),
        }

    async def _get_context_features(self, fixture: Fixture) -> Dict:
        """Extract context features (derby, top6 clash, etc.)"""

        # Derby check (same city)
        home_team_stmt = select(Team).where(Team.id == fixture.home_team_id)
        home_team = (await self.session.execute(home_team_stmt)).scalar_one()

        away_team_stmt = select(Team).where(Team.id == fixture.away_team_id)
        away_team = (await self.session.execute(away_team_stmt)).scalar_one()

        # Simple derby detection (TODO: improve with city mapping)
        derby_pairs = [
            ('Inter', 'AC Milan'),
            ('Roma', 'Lazio'),
            ('Juventus', 'Torino'),
        ]

        is_derby = any(
            (home_team.name in pair and away_team.name in pair)
            for pair in derby_pairs
        )

        return {
            'is_derby': 1.0 if is_derby else 0.0,
            'is_top6_clash': 0.0,  # TODO: Calculate based on standings
            'days_since_last_match_home': 0,  # TODO: Calculate
            'days_since_last_match_away': 0,  # TODO: Calculate
        }
