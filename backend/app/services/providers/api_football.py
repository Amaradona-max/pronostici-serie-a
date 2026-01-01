"""
API-Football Provider
Primary data source for Serie A fixtures, stats, injuries
Documentation: https://www.api-football.com/documentation-v3
"""

import httpx
from typing import List, Dict, Optional
from datetime import datetime
import logging
from app.services.providers.base import (
    BaseDataProvider,
    MatchData,
    InjuryData,
    TeamStatsData
)
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class APIFootballAdapter(BaseDataProvider):
    """
    Adapter for API-Football (RapidAPI)

    Provides comprehensive football data including:
    - Fixtures and results
    - Team and player statistics
    - Injuries and lineups
    - Live match data
    """

    BASE_URL = "https://v3.football.api-sports.io"
    SERIE_A_ID = 135  # Serie A league ID on API-Football
    SERIE_A_SEASON = 2025  # Current season

    # Team ID mapping (API-Football IDs for Serie A 2025/26 teams)
    TEAM_MAPPING = {
        'Inter': 505,
        'AC Milan': 489,
        'Juventus': 496,
        'Napoli': 492,
        'AS Roma': 497,
        'Lazio': 487,
        'Atalanta': 499,
        'Fiorentina': 502,
        'Bologna': 500,
        'Torino': 503,
        'Udinese': 494,
        'Empoli': 511,
        'Sassuolo': 488,
        'Cagliari': 490,
        'Verona': 504,
        'Lecce': 867,
        'Monza': 1579,
        'Salernitana': 514,
        'Como': 512,
        'Parma': 491,
    }

    def __init__(self):
        self.api_key = settings.API_FOOTBALL_KEY
        self.client = httpx.AsyncClient(
            headers={
                'x-rapidapi-host': 'v3.football.api-sports.io',
                'x-rapidapi-key': self.api_key
            },
            timeout=30.0
        )
        self._request_count = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make HTTP request to API-Football with error handling.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response dict

        Raises:
            Exception: On API errors
        """
        url = f"{self.BASE_URL}/{endpoint}"

        try:
            logger.info(f"API-Football request: {endpoint} with params {params}")
            response = await self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            # Check API response structure
            if 'errors' in data and data['errors']:
                raise Exception(f"API-Football error: {data['errors']}")

            self._request_count += 1
            logger.info(f"API-Football request #{self._request_count} successful")

            return data

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from API-Football: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Error calling API-Football: {str(e)}")
            raise

    async def get_fixtures(self, competition_id: int, season: str) -> List[MatchData]:
        """Retrieve all fixtures for Serie A season"""

        # Convert season string to year (2025-2026 -> 2025)
        season_year = int(season.split('-')[0])

        params = {
            'league': self.SERIE_A_ID,
            'season': season_year
        }

        data = await self._make_request('fixtures', params)

        fixtures = []
        for item in data.get('response', []):
            fixture = item['fixture']
            teams = item['teams']
            goals = item['goals']
            league = item['league']

            fixtures.append(MatchData(
                external_id=fixture['id'],
                home_team_id=teams['home']['id'],
                away_team_id=teams['away']['id'],
                match_date=datetime.fromisoformat(fixture['date'].replace('Z', '+00:00')),
                status=self._map_status(fixture['status']['short']),
                home_score=goals['home'],
                away_score=goals['away'],
                venue=fixture['venue']['name'] if fixture.get('venue') else None,
                round=league.get('round')
            ))

        logger.info(f"Retrieved {len(fixtures)} fixtures from API-Football")
        return fixtures

    async def get_live_fixtures(self) -> List[MatchData]:
        """Retrieve currently live fixtures for Serie A"""
        
        params = {
            'league': self.SERIE_A_ID,
            'live': 'all'
        }

        data = await self._make_request('fixtures', params)

        fixtures = []
        for item in data.get('response', []):
            fixture = item['fixture']
            teams = item['teams']
            goals = item['goals']
            league = item['league']

            fixtures.append(MatchData(
                external_id=fixture['id'],
                home_team_id=teams['home']['id'],
                away_team_id=teams['away']['id'],
                match_date=datetime.fromisoformat(fixture['date'].replace('Z', '+00:00')),
                status=self._map_status(fixture['status']['short']),
                home_score=goals['home'],
                away_score=goals['away'],
                venue=fixture['venue']['name'] if fixture.get('venue') else None,
                round=league.get('round')
            ))

        logger.info(f"Retrieved {len(fixtures)} live fixtures from API-Football")
        return fixtures

    async def get_match_details(self, match_id: int) -> MatchData:
        """Get details for a specific match"""

        params = {'id': match_id}
        data = await self._make_request('fixtures', params)

        if not data.get('response'):
            raise ValueError(f"Match {match_id} not found")

        item = data['response'][0]
        fixture = item['fixture']
        teams = item['teams']
        goals = item['goals']
        league = item['league']

        return MatchData(
            external_id=fixture['id'],
            home_team_id=teams['home']['id'],
            away_team_id=teams['away']['id'],
            match_date=datetime.fromisoformat(fixture['date'].replace('Z', '+00:00')),
            status=self._map_status(fixture['status']['short']),
            home_score=goals['home'],
            away_score=goals['away'],
            venue=fixture['venue']['name'] if fixture.get('venue') else None,
            round=league.get('round')
        )

    async def get_injuries(self, team_id: int) -> List[InjuryData]:
        """Get current injuries for a team"""

        params = {
            'team': team_id,
            'season': self.SERIE_A_SEASON,
            'league': self.SERIE_A_ID
        }

        data = await self._make_request('injuries', params)

        injuries = []
        for item in data.get('response', []):
            player = item['player']

            injuries.append(InjuryData(
                player_external_id=player['id'],
                player_name=player['name'],
                team_external_id=team_id,
                injury_type=player.get('reason', 'Unknown'),
                severity=self._map_injury_severity(player.get('reason', '')),
                expected_return=None  # API-Football doesn't provide this
            ))

        logger.info(f"Retrieved {len(injuries)} injuries for team {team_id}")
        return injuries

    async def get_team_stats(self, team_id: int, season: str) -> TeamStatsData:
        """Get season statistics for a team"""

        season_year = int(season.split('-')[0])

        params = {
            'team': team_id,
            'season': season_year,
            'league': self.SERIE_A_ID
        }

        data = await self._make_request('teams/statistics', params)

        if not data.get('response'):
            # Return default stats if not available
            return TeamStatsData(
                team_external_id=team_id,
                matches_played=0,
                wins=0,
                draws=0,
                losses=0,
                goals_scored=0,
                goals_conceded=0
            )

        stats = data['response']
        fixtures = stats.get('fixtures', {})
        goals = stats.get('goals', {})

        return TeamStatsData(
            team_external_id=team_id,
            matches_played=fixtures.get('played', {}).get('total', 0),
            wins=fixtures.get('wins', {}).get('total', 0),
            draws=fixtures.get('draws', {}).get('total', 0),
            losses=fixtures.get('loses', {}).get('total', 0),
            goals_scored=goals.get('for', {}).get('total', {}).get('total', 0),
            goals_conceded=goals.get('against', {}).get('total', {}).get('total', 0),
            xg_for=0.0,  # Not provided by API-Football free tier
            xg_against=0.0,
            avg_possession=0.0
        )

    async def get_h2h(self, team1_id: int, team2_id: int, limit: int = 10) -> List[MatchData]:
        """Get head-to-head matches between two teams"""

        params = {
            'h2h': f"{team1_id}-{team2_id}",
            'last': limit
        }

        data = await self._make_request('fixtures/headtohead', params)

        matches = []
        for item in data.get('response', []):
            fixture = item['fixture']
            teams = item['teams']
            goals = item['goals']
            league = item['league']

            matches.append(MatchData(
                external_id=fixture['id'],
                home_team_id=teams['home']['id'],
                away_team_id=teams['away']['id'],
                match_date=datetime.fromisoformat(fixture['date'].replace('Z', '+00:00')),
                status=self._map_status(fixture['status']['short']),
                home_score=goals['home'],
                away_score=goals['away'],
                venue=fixture['venue']['name'] if fixture.get('venue') else None,
                round=league.get('round')
            ))

        return matches

    def _map_status(self, api_status: str) -> str:
        """Map API-Football status codes to internal status"""
        mapping = {
            'TBD': 'scheduled',
            'NS': 'scheduled',
            '1H': 'live',
            'HT': 'live',
            '2H': 'live',
            'ET': 'live',
            'P': 'live',
            'FT': 'finished',
            'AET': 'finished',
            'PEN': 'finished',
            'PST': 'postponed',
            'CANC': 'cancelled',
            'ABD': 'cancelled',
            'AWD': 'finished',
            'WO': 'finished'
        }
        return mapping.get(api_status, 'scheduled')

    def _map_injury_severity(self, injury_reason: str) -> str:
        """
        Map injury description to severity level.
        Heuristic based on common keywords.
        """
        reason_lower = injury_reason.lower()

        # Severe injuries (3+ months)
        severe_keywords = ['acl', 'cruciate', 'fracture', 'surgery', 'rupture', 'broken']
        if any(word in reason_lower for word in severe_keywords):
            return 'severe'

        # Major injuries (1-3 months)
        major_keywords = ['muscle', 'hamstring', 'groin', 'thigh', 'calf', 'ligament']
        if any(word in reason_lower for word in major_keywords):
            return 'major'

        # Moderate injuries (2-4 weeks)
        moderate_keywords = ['ankle', 'knee', 'back', 'shoulder', 'strain']
        if any(word in reason_lower for word in moderate_keywords):
            return 'moderate'

        # Minor injuries (< 2 weeks)
        return 'minor'

    @property
    def rate_limit_config(self) -> Dict:
        """Rate limiting configuration"""
        return {
            'max_requests': 100,  # Free tier
            'time_window': 86400,  # 24 hours
            'tier': 'free'
        }

    @property
    def provider_name(self) -> str:
        return "api_football"
