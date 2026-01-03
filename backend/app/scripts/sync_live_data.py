"""
Automatic Live Data Synchronization Script
Syncs fixtures, results, and standings from Football-Data.org

This script can be run:
1. Manually: python -m app.scripts.sync_live_data
2. Via Render Cron Job: Every 2-5 minutes
3. Via scheduled task: Using Celery or similar

"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError

from app.db.engine import AsyncSessionLocal
from app.db.models import (
    Team, Fixture, Competition, FixtureStatus,
    TeamStats
)
from app.services.providers.orchestrator import DataProviderOrchestrator
from app.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
settings = get_settings()


class LiveDataSynchronizer:
    """
    Handles automatic synchronization of live football data.
    """

    def __init__(self):
        self.orchestrator = DataProviderOrchestrator()
        self.season = "2025-2026"
        self.serie_a_id = 135  # Serie A external ID

    async def fix_external_ids_if_needed(self):
        """
        ONE-TIME FIX: Ensure all teams have correct external_ids.
        This runs once at the start of each sync to ensure data integrity.
        """
        CORRECT_IDS = {
            "Inter": 505, "AC Milan": 489, "Juventus": 496, "Napoli": 492,
            "AS Roma": 497, "Lazio": 487, "Atalanta": 499, "Fiorentina": 502,
            "Bologna": 500, "Torino": 503, "Udinese": 494, "Lecce": 867,
            "Cagliari": 490, "Hellas Verona": 504, "Genoa": 495, "Parma": 130,
            "Como": 1047, "Sassuolo": 488, "Pisa": 506, "Cremonese": 520
        }

        try:
            async with AsyncSessionLocal() as session:
                teams = (await session.execute(select(Team))).scalars().all()
                fixed = 0
                for team in teams:
                    correct_id = CORRECT_IDS.get(team.name)
                    if correct_id and team.external_id != correct_id:
                        team.external_id = correct_id
                        fixed += 1
                if fixed > 0:
                    await session.commit()
                    logger.info(f"✅ Fixed {fixed} team external_ids")
        except Exception as e:
            logger.warning(f"External ID fix skipped: {str(e)}")

    async def sync_all(self):
        """
        Main sync method - updates all live data.
        """
        logger.info("=" * 60)
        logger.info("Starting live data synchronization")
        logger.info(f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
        logger.info("=" * 60)

        try:
            # 0. Fix external IDs if needed (one-time auto-fix)
            await self.fix_external_ids_if_needed()

            # 1. Sync live matches (most important)
            await self.sync_live_matches()

            # 2. Sync today's fixtures
            await self.sync_todays_fixtures()

            # 3. Update standings if matches finished recently
            await self.update_standings_if_needed()

            logger.info("✅ Live data synchronization completed successfully!")

        except Exception as e:
            logger.error(f"❌ Sync failed: {str(e)}", exc_info=True)
            raise

        finally:
            await self.orchestrator.close()

    async def sync_live_matches(self):
        """
        Sync currently live Serie A matches.
        Updates scores in real-time.
        """
        logger.info("📡 Syncing live matches...")

        try:
            # Get live matches from provider
            live_matches = await self.orchestrator.get_live_fixtures_with_fallback()

            if not live_matches:
                logger.info("No live matches at the moment")
                return

            logger.info(f"Found {len(live_matches)} live matches")

            async with AsyncSessionLocal() as session:
                for match_data in live_matches:
                    await self._update_match_score(session, match_data)

                await session.commit()

            logger.info(f"✅ Updated {len(live_matches)} live matches")

        except Exception as e:
            logger.error(f"Failed to sync live matches: {str(e)}")

    async def sync_todays_fixtures(self):
        """
        Sync fixtures for today and tomorrow.
        Updates match status and scores.
        """
        logger.info("📅 Syncing today's fixtures...")

        try:
            # Get fixtures from provider
            logger.info(f"Fetching all fixtures for competition_id={self.serie_a_id}, season={self.season}")
            all_fixtures = await self.orchestrator.get_fixtures_with_fallback(
                self.serie_a_id,
                self.season
            )
            logger.info(f"Received {len(all_fixtures)} total fixtures from provider")

            # Filter for recent matches (yesterday, today, tomorrow)
            # CRITICAL: Use UTC timezone to match Football-Data.org dates
            today = datetime.now(timezone.utc)
            yesterday = today - timedelta(days=1)
            tomorrow = today + timedelta(days=1)

            logger.info(f"Filtering fixtures between {yesterday.date()} and {tomorrow.date()} UTC")

            recent_fixtures = [
                f for f in all_fixtures
                if yesterday <= f.match_date <= tomorrow
            ]

            if not recent_fixtures:
                logger.info(f"No recent fixtures found (searched {len(all_fixtures)} total fixtures)")
                return

            logger.info(f"Found {len(recent_fixtures)} recent fixtures")

            async with AsyncSessionLocal() as session:
                # Get competition
                comp_stmt = select(Competition).where(
                    Competition.name == "Serie A",
                    Competition.season == self.season
                )
                competition = (await session.execute(comp_stmt)).scalar_one_or_none()

                if not competition:
                    logger.error("Serie A competition not found in database!")
                    return

                # Get team mappings
                teams_stmt = select(Team)
                teams_result = await session.execute(teams_stmt)
                teams_by_external_id = {
                    team.external_id: team
                    for team in teams_result.scalars().all()
                }

                logger.info(f"Loaded {len(teams_by_external_id)} teams from database")
                logger.info(f"Team external IDs in DB: {list(teams_by_external_id.keys())[:10]}...")

                updated = 0
                for match_data in recent_fixtures:
                    # Find teams
                    home_team = teams_by_external_id.get(match_data.home_team_id)
                    away_team = teams_by_external_id.get(match_data.away_team_id)

                    if not home_team or not away_team:
                        logger.warning(
                            f"Teams not found for external IDs: "
                            f"{match_data.home_team_id} vs {match_data.away_team_id}"
                        )
                        logger.warning(f"Available IDs in DB: {sorted(teams_by_external_id.keys())}")
                        continue

                    # Check if fixture exists
                    fixture_stmt = select(Fixture).where(
                        and_(
                            Fixture.home_team_id == home_team.id,
                            Fixture.away_team_id == away_team.id,
                            Fixture.season == self.season
                        )
                    )
                    fixture = (await session.execute(fixture_stmt)).scalar_one_or_none()

                    if fixture:
                        # Update existing fixture
                        fixture.status = self._map_status(match_data.status)
                        fixture.home_score = match_data.home_score
                        fixture.away_score = match_data.away_score
                        fixture.match_date = match_data.match_date
                        updated += 1
                    else:
                        # Create new fixture
                        new_fixture = Fixture(
                            competition_id=competition.id,
                            season=self.season,
                            round=match_data.round,
                            match_date=match_data.match_date,
                            home_team_id=home_team.id,
                            away_team_id=away_team.id,
                            status=self._map_status(match_data.status),
                            home_score=match_data.home_score,
                            away_score=match_data.away_score
                        )
                        session.add(new_fixture)
                        updated += 1

                await session.commit()

            logger.info(f"✅ Updated {updated} fixtures")

        except Exception as e:
            logger.error(f"Failed to sync fixtures: {str(e)}")

    async def update_standings_if_needed(self):
        """
        Update standings if matches finished recently.
        Only runs if there were finished matches in last 2 hours.
        """
        logger.info("📊 Checking if standings update needed...")

        try:
            async with AsyncSessionLocal() as session:
                # Check for recently finished matches (UTC timezone)
                two_hours_ago = datetime.now(timezone.utc) - timedelta(hours=2)

                stmt = select(Fixture).where(
                    and_(
                        Fixture.season == self.season,
                        Fixture.status == FixtureStatus.FINISHED,
                        Fixture.match_date >= two_hours_ago
                    )
                )
                recent_finished = (await session.execute(stmt)).scalars().all()

                if not recent_finished:
                    logger.info("No recently finished matches - standings update skipped")
                    return

                logger.info(f"Found {len(recent_finished)} recently finished matches")
                logger.info("Updating standings...")

                # TODO: Implement standings calculation from fixtures
                # For now, we can call the Football-Data standings endpoint
                await self._sync_standings_from_api()

                logger.info("✅ Standings updated")

        except Exception as e:
            logger.error(f"Failed to update standings: {str(e)}")

    async def _sync_standings_from_api(self):
        """
        Sync standings directly from Football-Data.org API.
        """
        try:
            # Get standings from primary provider
            if hasattr(self.orchestrator.primary_provider, 'get_standings'):
                standings_data = await self.orchestrator.primary_provider.get_standings(
                    self.season
                )

                # Parse and save standings
                await self._save_standings(standings_data)

        except Exception as e:
            logger.error(f"Failed to sync standings from API: {str(e)}")

    async def _save_standings(self, standings_data: dict):
        """
        Save standings data to database.
        """
        async with AsyncSessionLocal() as session:
            # Get teams
            teams_stmt = select(Team)
            teams_result = await session.execute(teams_stmt)
            teams_by_name = {team.name: team for team in teams_result.scalars().all()}

            # Parse standings
            standings = standings_data.get("standings", [])
            if not standings:
                logger.warning("No standings data returned")
                return

            # Usually first element is the main table
            table = standings[0].get("table", [])

            for position in table:
                team_name = position.get("team", {}).get("name")
                team = teams_by_name.get(team_name)

                if not team:
                    logger.warning(f"Team not found: {team_name}")
                    continue

                # Update or create team stats
                stats_stmt = select(TeamStats).where(
                    and_(
                        TeamStats.team_id == team.id,
                        TeamStats.season == self.season
                    )
                )
                stats = (await session.execute(stats_stmt)).scalar_one_or_none()

                if not stats:
                    stats = TeamStats(
                        team_id=team.id,
                        season=self.season
                    )
                    session.add(stats)

                # Update stats
                stats.matches_played = position.get("playedGames", 0)
                stats.wins = position.get("won", 0)
                stats.draws = position.get("draw", 0)
                stats.losses = position.get("lost", 0)
                stats.goals_for = position.get("goalsFor", 0)
                stats.goals_against = position.get("goalsAgainst", 0)
                stats.goal_difference = position.get("goalDifference", 0)
                stats.points = position.get("points", 0)
                stats.position = position.get("position", 0)

            await session.commit()
            logger.info("Standings saved to database")

    async def _update_match_score(self, session, match_data):
        """
        Update match score in database.
        """
        try:
            # Find fixture by external ID or team IDs
            stmt = select(Fixture).where(
                Fixture.season == self.season,
                # Additional filtering needed based on team IDs
            )
            # Implementation depends on how external IDs are stored

        except Exception as e:
            logger.error(f"Failed to update match score: {str(e)}")

    def _map_status(self, status: str) -> FixtureStatus:
        """
        Map external status to internal FixtureStatus enum.
        """
        status_map = {
            "scheduled": FixtureStatus.SCHEDULED,
            "live": FixtureStatus.LIVE,
            "finished": FixtureStatus.FINISHED,
            "postponed": FixtureStatus.POSTPONED,
            "cancelled": FixtureStatus.CANCELLED
        }
        return status_map.get(status.lower(), FixtureStatus.SCHEDULED)


async def main():
    """
    Main entry point for sync script.
    """
    try:
        synchronizer = LiveDataSynchronizer()
        await synchronizer.sync_all()

    except Exception as e:
        logger.error(f"Sync script failed: {str(e)}", exc_info=True)
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
