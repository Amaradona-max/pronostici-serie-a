"""
Data Provider Orchestrator
Coordinates multiple data providers with fallback strategy
"""

import logging
from typing import List, Optional
from app.services.providers.base import (
    BaseDataProvider,
    MatchData,
    InjuryData,
    TeamStatsData
)
from app.services.providers.football_data import FootballDataAdapter
from app.services.providers.api_football import APIFootballAdapter
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class DataProviderOrchestrator:
    """
    Orchestrates data retrieval from multiple providers.

    Features:
    - Primary/fallback provider strategy (Football-Data.org -> API-Football)
    - Automatic retry on failure
    - Logging and monitoring
    - Rate limit management
    """

    def __init__(self):
        """
        Initialize providers based on available API keys.

        Priority:
        1. Football-Data.org (free, 10 req/min, Serie A included)
        2. API-Football (fallback, paid/free tier)
        """
        # Try to use Football-Data as primary if key available
        if settings.FOOTBALL_DATA_KEY:
            self.primary_provider: BaseDataProvider = FootballDataAdapter()
            logger.info("Using Football-Data.org as primary provider")

            # API-Football as fallback if key available
            if settings.API_FOOTBALL_KEY:
                self.fallback_provider: Optional[BaseDataProvider] = APIFootballAdapter()
                logger.info("API-Football configured as fallback provider")
            else:
                self.fallback_provider = None
                logger.warning("No fallback provider configured")

        # Fall back to API-Football if Football-Data not available
        elif settings.API_FOOTBALL_KEY:
            self.primary_provider: BaseDataProvider = APIFootballAdapter()
            self.fallback_provider = None
            logger.warning("Using API-Football as primary (no Football-Data key)")

        else:
            raise Exception("No API keys configured! Please set FOOTBALL_DATA_KEY or API_FOOTBALL_KEY")

    async def get_fixtures_with_fallback(
        self,
        competition_id: int,
        season: str
    ) -> List[MatchData]:
        """
        Get fixtures with automatic fallback to secondary provider.

        Args:
            competition_id: External competition ID
            season: Season string

        Returns:
            List of MatchData

        Raises:
            Exception: If all providers fail
        """
        try:
            logger.info(f"Fetching fixtures from primary provider for season {season}")
            fixtures = await self.primary_provider.get_fixtures(competition_id, season)
            logger.info(f"Successfully retrieved {len(fixtures)} fixtures from primary")
            return fixtures

        except Exception as primary_error:
            logger.warning(
                f"Primary provider failed: {str(primary_error)}. "
                f"Attempting fallback..."
            )

            if self.fallback_provider:
                try:
                    fixtures = await self.fallback_provider.get_fixtures(
                        competition_id,
                        season
                    )
                    logger.info(
                        f"Successfully retrieved {len(fixtures)} fixtures from fallback"
                    )
                    return fixtures
                except Exception as fallback_error:
                    logger.error(f"Fallback provider also failed: {str(fallback_error)}")
                    raise Exception("All data providers failed") from fallback_error
            else:
                logger.error("No fallback provider configured")
                raise Exception("Primary provider failed and no fallback available")

    async def get_live_fixtures_with_fallback(self) -> List[MatchData]:
        """
        Get live fixtures with automatic fallback to secondary provider.
        """
        try:
            logger.info("Fetching live fixtures from primary provider")
            fixtures = await self.primary_provider.get_live_fixtures()
            logger.info(f"Successfully retrieved {len(fixtures)} live fixtures from primary")
            return fixtures

        except Exception as primary_error:
            logger.warning(
                f"Primary provider failed for live fixtures: {str(primary_error)}. "
                f"Attempting fallback..."
            )

            if self.fallback_provider:
                try:
                    fixtures = await self.fallback_provider.get_live_fixtures()
                    logger.info(
                        f"Successfully retrieved {len(fixtures)} live fixtures from fallback"
                    )
                    return fixtures
                except Exception as fallback_error:
                    logger.error(f"Fallback provider also failed for live fixtures: {str(fallback_error)}")
                    # For live fixtures, it's better to return empty list than crash
                    return []
            else:
                logger.error("No fallback provider configured for live fixtures")
                return []

    async def get_injuries_with_fallback(
        self,
        team_id: int
    ) -> List[InjuryData]:
        """Get injuries with fallback"""

        try:
            injuries = await self.primary_provider.get_injuries(team_id)
            logger.info(f"Retrieved {len(injuries)} injuries for team {team_id}")
            return injuries

        except Exception as e:
            logger.warning(f"Failed to get injuries from primary: {str(e)}")

            if self.fallback_provider:
                try:
                    return await self.fallback_provider.get_injuries(team_id)
                except Exception:
                    logger.error("Fallback provider also failed for injuries")
                    return []  # Return empty list instead of failing
            else:
                logger.warning("Returning empty injuries list (no fallback)")
                return []

    async def get_team_stats_with_fallback(
        self,
        team_id: int,
        season: str
    ) -> TeamStatsData:
        """Get team stats with fallback"""

        try:
            stats = await self.primary_provider.get_team_stats(team_id, season)
            return stats

        except Exception as e:
            logger.warning(f"Failed to get team stats from primary: {str(e)}")

            if self.fallback_provider:
                try:
                    return await self.fallback_provider.get_team_stats(team_id, season)
                except Exception:
                    logger.error("Fallback provider also failed for stats")
                    # Return default stats
                    return TeamStatsData(
                        team_external_id=team_id,
                        matches_played=0,
                        wins=0,
                        draws=0,
                        losses=0,
                        goals_scored=0,
                        goals_conceded=0
                    )
            else:
                # Return default stats if no fallback
                return TeamStatsData(
                    team_external_id=team_id,
                    matches_played=0,
                    wins=0,
                    draws=0,
                    losses=0,
                    goals_scored=0,
                    goals_conceded=0
                )

    async def get_h2h_with_fallback(
        self,
        team1_id: int,
        team2_id: int,
        limit: int = 10
    ) -> List[MatchData]:
        """Get head-to-head matches with fallback"""

        try:
            matches = await self.primary_provider.get_h2h(team1_id, team2_id, limit)
            return matches

        except Exception as e:
            logger.warning(f"Failed to get H2H from primary: {str(e)}")

            if self.fallback_provider:
                try:
                    return await self.fallback_provider.get_h2h(team1_id, team2_id, limit)
                except Exception:
                    logger.error("Fallback provider also failed for H2H")
                    return []
            else:
                return []

    async def close(self):
        """Close all provider connections"""
        if hasattr(self.primary_provider, 'client'):
            await self.primary_provider.client.aclose()
        if self.fallback_provider and hasattr(self.fallback_provider, 'client'):
            await self.fallback_provider.client.aclose()
