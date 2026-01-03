"""
Football-Data.org Provider
Free, reliable data source for Serie A with generous rate limits
Documentation: https://www.football-data.org/documentation/api
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


class FootballDataAdapter(BaseDataProvider):
    """
    Adapter for Football-Data.org API

    Features:
    - Free tier: 10 requests/minute (14,400/day)
    - Serie A included in free tier FOREVER
    - Reliable and well-maintained
    - Updates every 2-3 minutes
    """

    BASE_URL = "https://api.football-data.org/v4"
    SERIE_A_CODE = "SA"  # Serie A competition code
    SERIE_A_ID = 2019    # Serie A competition ID

    # Team ID mapping: Football-Data.org ID → API-Football ID (used in database)
    # This mapping allows us to match teams between providers
    TEAM_MAPPING = {
        108: 505,   # Inter
        98: 489,    # AC Milan
        109: 496,   # Juventus
        113: 492,   # Napoli
        100: 497,   # AS Roma
        110: 487,   # Lazio
        102: 499,   # Atalanta
        99: 502,    # Fiorentina
        103: 500,   # Bologna
        586: 503,   # Torino
        115: 494,   # Udinese
        5890: 867,  # Lecce
        104: 490,   # Cagliari
        450: 504,   # Hellas Verona
        107: 495,   # Genoa
        112: 130,   # Parma
        7397: 1047, # Como
        471: 488,   # Sassuolo
        487: 506,   # Pisa
        457: 520,   # Cremonese
    }

    def __init__(self):
        self.api_key = settings.FOOTBALL_DATA_KEY
        self.client = httpx.AsyncClient(
            headers={
                'X-Auth-Token': self.api_key
            },
            timeout=30.0
        )
        self._request_count = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    @property
    def provider_name(self) -> str:
        return "football-data.org"

    @property
    def rate_limit_config(self) -> Dict:
        """
        Free tier rate limits:
        - 10 requests per minute
        - 14,400 requests per day
        """
        return {
            "max_requests": 10,
            "time_window": 60,  # seconds
            "tier": "free"
        }

    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make HTTP request to Football-Data.org with error handling.

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
            logger.info(f"Football-Data.org request: {endpoint} with params {params}")
            response = await self.client.get(url, params=params)

            # Track rate limiting
            self._request_count += 1
            remaining = response.headers.get('X-Requests-Available-Minute', 'unknown')
            logger.debug(f"Rate limit - Requests remaining this minute: {remaining}")

            response.raise_for_status()
            data = response.json()

            logger.info(f"Football-Data.org request successful")
            return data

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.error("Football-Data.org rate limit exceeded")
                raise Exception("Rate limit exceeded - too many requests")
            elif e.response.status_code == 403:
                logger.error("Football-Data.org API key invalid or access denied")
                raise Exception("Invalid API key or access denied")
            else:
                logger.error(f"Football-Data.org HTTP error: {e}")
                raise Exception(f"API error: {e.response.status_code}")

        except Exception as e:
            logger.error(f"Football-Data.org request failed: {str(e)}")
            raise

    async def get_fixtures(self, competition_id: int, season: str) -> List[MatchData]:
        """
        Get all fixtures for Serie A season.

        Args:
            competition_id: Ignored (we use SERIE_A_CODE)
            season: Season string (e.g., "2025-2026")

        Returns:
            List of MatchData objects
        """
        try:
            # Convert season format: "2025-2026" -> 2025
            season_year = int(season.split("-")[0])

            # Get all matches for the season
            data = await self._make_request(
                f"competitions/{self.SERIE_A_CODE}/matches",
                params={"season": season_year}
            )

            matches = []
            for match in data.get("matches", []):
                match_data = self._parse_match(match)
                if match_data:
                    matches.append(match_data)

            logger.info(f"Retrieved {len(matches)} fixtures for Serie A {season}")
            return matches

        except Exception as e:
            logger.error(f"Failed to get fixtures: {str(e)}")
            raise

    async def get_live_fixtures(self) -> List[MatchData]:
        """
        Get currently live Serie A fixtures.

        Returns:
            List of MatchData for live matches
        """
        try:
            # Get today's matches
            data = await self._make_request(
                "matches",
                params={"competitions": self.SERIE_A_ID}
            )

            live_matches = []
            for match in data.get("matches", []):
                if match.get("status") in ["IN_PLAY", "PAUSED", "LIVE"]:
                    match_data = self._parse_match(match)
                    if match_data:
                        live_matches.append(match_data)

            logger.info(f"Retrieved {len(live_matches)} live Serie A matches")
            return live_matches

        except Exception as e:
            logger.error(f"Failed to get live fixtures: {str(e)}")
            return []

    async def get_match_details(self, match_id: int) -> MatchData:
        """
        Get detailed information for a single match.

        Args:
            match_id: Football-Data.org match ID

        Returns:
            MatchData object
        """
        try:
            data = await self._make_request(f"matches/{match_id}")
            match_data = self._parse_match(data)

            if not match_data:
                raise Exception(f"Failed to parse match {match_id}")

            return match_data

        except Exception as e:
            logger.error(f"Failed to get match details: {str(e)}")
            raise

    async def get_team_stats(self, team_id: int, season: str) -> TeamStatsData:
        """
        Get season statistics for a team.

        Args:
            team_id: Football-Data.org team ID
            season: Season string

        Returns:
            TeamStatsData object
        """
        try:
            season_year = int(season.split("-")[0])

            # Get team matches to calculate stats
            data = await self._make_request(
                f"teams/{team_id}/matches",
                params={
                    "season": season_year,
                    "competitions": self.SERIE_A_ID
                }
            )

            # Calculate stats from matches
            matches = data.get("matches", [])
            stats = self._calculate_team_stats(team_id, matches)

            return stats

        except Exception as e:
            logger.error(f"Failed to get team stats: {str(e)}")
            # Return default stats on error
            return TeamStatsData(
                team_external_id=team_id,
                matches_played=0,
                wins=0,
                draws=0,
                losses=0,
                goals_scored=0,
                goals_conceded=0
            )

    async def get_injuries(self, team_id: int) -> List[InjuryData]:
        """
        Get current injuries for a team.

        Note: Football-Data.org free tier doesn't include injury data.
        This returns empty list.

        Args:
            team_id: Team external ID

        Returns:
            Empty list (injuries not available in free tier)
        """
        logger.warning("Injury data not available in Football-Data.org free tier")
        return []

    async def get_h2h(self, team1_id: int, team2_id: int, limit: int = 10) -> List[MatchData]:
        """
        Get head-to-head matches between two teams.

        Args:
            team1_id: First team ID
            team2_id: Second team ID
            limit: Maximum matches to return

        Returns:
            List of MatchData objects
        """
        try:
            # Get team1 matches
            data = await self._make_request(
                f"teams/{team1_id}/matches",
                params={"limit": 50}  # Get more to filter H2H
            )

            h2h_matches = []
            for match in data.get("matches", []):
                home_id = match.get("homeTeam", {}).get("id")
                away_id = match.get("awayTeam", {}).get("id")

                # Check if both teams are in this match
                if (home_id == team1_id and away_id == team2_id) or \
                   (home_id == team2_id and away_id == team1_id):
                    match_data = self._parse_match(match)
                    if match_data and match_data.status == "FINISHED":
                        h2h_matches.append(match_data)

                    if len(h2h_matches) >= limit:
                        break

            logger.info(f"Retrieved {len(h2h_matches)} H2H matches")
            return h2h_matches

        except Exception as e:
            logger.error(f"Failed to get H2H: {str(e)}")
            return []

    def _parse_match(self, match_data: Dict) -> Optional[MatchData]:
        """
        Parse match data from Football-Data.org format to MatchData.

        Args:
            match_data: Raw match dict from API

        Returns:
            MatchData object or None if parsing fails
        """
        try:
            # Extract match info
            match_id = match_data.get("id")
            home_team = match_data.get("homeTeam", {})
            away_team = match_data.get("awayTeam", {})
            utc_date = match_data.get("utcDate")
            status = match_data.get("status")
            score = match_data.get("score", {})

            # Parse date
            match_date = datetime.fromisoformat(utc_date.replace("Z", "+00:00"))

            # Parse scores
            full_time = score.get("fullTime", {})
            home_score = full_time.get("home")
            away_score = full_time.get("away")

            # Map status
            status_map = {
                "SCHEDULED": "scheduled",
                "TIMED": "scheduled",
                "IN_PLAY": "live",
                "PAUSED": "live",
                "FINISHED": "finished",
                "POSTPONED": "postponed",
                "CANCELLED": "cancelled"
            }
            mapped_status = status_map.get(status, "scheduled")

            # Extract matchday (round)
            matchday = match_data.get("matchday")
            round_str = f"Giornata {matchday}" if matchday else None

            # Map Football-Data.org team IDs to database external IDs
            fd_home_id = home_team.get("id")
            fd_away_id = away_team.get("id")

            # Use mapping, fallback to original ID if not found
            db_home_id = self.TEAM_MAPPING.get(fd_home_id, fd_home_id)
            db_away_id = self.TEAM_MAPPING.get(fd_away_id, fd_away_id)

            return MatchData(
                external_id=match_id,
                home_team_id=db_home_id,
                away_team_id=db_away_id,
                match_date=match_date,
                status=mapped_status,
                home_score=home_score,
                away_score=away_score,
                venue=match_data.get("venue"),
                round=round_str
            )

        except Exception as e:
            logger.error(f"Failed to parse match: {str(e)}")
            return None

    def _calculate_team_stats(self, team_id: int, matches: List[Dict]) -> TeamStatsData:
        """
        Calculate team statistics from match history.

        Args:
            team_id: Team ID
            matches: List of match dicts

        Returns:
            TeamStatsData object
        """
        wins = draws = losses = 0
        goals_for = goals_against = 0
        matches_played = 0

        for match in matches:
            if match.get("status") != "FINISHED":
                continue

            # Get Football-Data.org IDs and map them to database IDs
            fd_home_id = match.get("homeTeam", {}).get("id")
            fd_away_id = match.get("awayTeam", {}).get("id")
            home_team_id = self.TEAM_MAPPING.get(fd_home_id, fd_home_id)
            away_team_id = self.TEAM_MAPPING.get(fd_away_id, fd_away_id)
            score = match.get("score", {}).get("fullTime", {})
            home_score = score.get("home")
            away_score = score.get("away")

            if home_score is None or away_score is None:
                continue

            matches_played += 1

            if home_team_id == team_id:
                goals_for += home_score
                goals_against += away_score
                if home_score > away_score:
                    wins += 1
                elif home_score == away_score:
                    draws += 1
                else:
                    losses += 1

            elif away_team_id == team_id:
                goals_for += away_score
                goals_against += home_score
                if away_score > home_score:
                    wins += 1
                elif away_score == home_score:
                    draws += 1
                else:
                    losses += 1

        return TeamStatsData(
            team_external_id=team_id,
            matches_played=matches_played,
            wins=wins,
            draws=draws,
            losses=losses,
            goals_scored=goals_for,
            goals_conceded=goals_against
        )

    async def get_standings(self, season: str) -> Dict:
        """
        Get Serie A standings for the season.

        Args:
            season: Season string (e.g., "2025-2026")

        Returns:
            Standings data dict
        """
        try:
            season_year = int(season.split("-")[0])

            data = await self._make_request(
                f"competitions/{self.SERIE_A_CODE}/standings",
                params={"season": season_year}
            )

            return data

        except Exception as e:
            logger.error(f"Failed to get standings: {str(e)}")
            raise

    async def close(self):
        """Close HTTP client connection"""
        await self.client.aclose()
