"""
Base Data Provider Interface
Abstract class for all external data providers
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MatchData:
    """Normalized match data structure across providers"""
    external_id: int
    home_team_id: int
    away_team_id: int
    match_date: datetime
    status: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    venue: Optional[str] = None
    round: Optional[str] = None


@dataclass
class InjuryData:
    """Normalized injury data structure"""
    player_external_id: int
    player_name: str
    team_external_id: int
    injury_type: str
    severity: str  # minor, moderate, major, severe
    expected_return: Optional[datetime] = None


@dataclass
class TeamStatsData:
    """Normalized team statistics structure"""
    team_external_id: int
    matches_played: int
    wins: int
    draws: int
    losses: int
    goals_scored: int
    goals_conceded: int
    xg_for: float = 0.0
    xg_against: float = 0.0
    avg_possession: float = 0.0


@dataclass
class LineupData:
    """Team lineup data"""
    team_external_id: int
    formation: Optional[str]
    players: List[Dict]


class BaseDataProvider(ABC):
    """
    Abstract base class for external data providers.
    All providers must implement these methods to ensure consistent interface.
    """

    @abstractmethod
    async def get_fixtures(self, competition_id: int, season: str) -> List[MatchData]:
        """
        Retrieve all fixtures for a competition and season.

        Args:
            competition_id: External competition ID
            season: Season string (e.g., "2025-2026")

        Returns:
            List of MatchData objects
        """
        pass

    @abstractmethod
    async def get_match_details(self, match_id: int) -> MatchData:
        """
        Get detailed information for a single match.

        Args:
            match_id: External match ID

        Returns:
            MatchData object
        """
        pass

    @abstractmethod
    async def get_injuries(self, team_id: int) -> List[InjuryData]:
        """
        Get current injuries for a team.

        Args:
            team_id: External team ID

        Returns:
            List of InjuryData objects
        """
        pass

    @abstractmethod
    async def get_team_stats(self, team_id: int, season: str) -> TeamStatsData:
        """
        Get season statistics for a team.

        Args:
            team_id: External team ID
            season: Season string

        Returns:
            TeamStatsData object
        """
        pass

    @abstractmethod
    async def get_h2h(self, team1_id: int, team2_id: int, limit: int = 10) -> List[MatchData]:
        """
        Get head-to-head match history between two teams.

        Args:
            team1_id: First team external ID
            team2_id: Second team external ID
            limit: Maximum number of matches to return

        Returns:
            List of MatchData objects
        """
        pass

    @property
    @abstractmethod
    def rate_limit_config(self) -> Dict:
        """
        Get rate limiting configuration for this provider.

        Returns:
            Dict with keys: max_requests, time_window, tier
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get provider name identifier"""
        pass
