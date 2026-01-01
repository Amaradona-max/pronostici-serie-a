"""
Celery Tasks for Data Synchronization
"""

from celery import shared_task
from sqlalchemy import select, and_, or_
from datetime import datetime, timedelta
import logging
import asyncio

from app.tasks.celery_app import celery_app
from app.db import models
from app.db.engine import AsyncSessionLocal
from app.services.providers.orchestrator import DataProviderOrchestrator
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def run_async(coroutine):
    """Helper to run async functions in Celery tasks"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coroutine)


@shared_task(bind=True, max_retries=3)
def sync_season_fixtures(self, season: str):
    """
    Sync all fixtures for a season from external API.

    Args:
        season: Season string (e.g., "2025-2026")
    """
    try:
        logger.info(f"Starting sync of fixtures for season {season}")

        async def _sync():
            async with AsyncSessionLocal() as session:
                orchestrator = DataProviderOrchestrator()

                try:
                    # Get fixtures from API
                    fixtures = await orchestrator.get_fixtures_with_fallback(
                        competition_id=135,  # Serie A
                        season=season
                    )

                    logger.info(f"Retrieved {len(fixtures)} fixtures from API")

                    # Save to database
                    saved_count = 0
                    for fixture_data in fixtures:
                        # Check if fixture exists
                        stmt = select(models.Fixture).where(
                            models.Fixture.external_id == fixture_data.external_id
                        )
                        existing = (await session.execute(stmt)).scalar_one_or_none()

                        if existing:
                            # Update existing
                            existing.match_date = fixture_data.match_date
                            existing.status = fixture_data.status
                            existing.home_score = fixture_data.home_score
                            existing.away_score = fixture_data.away_score
                            existing.last_synced_at = datetime.utcnow()
                        else:
                            # Create new fixture
                            # First, get or create competition
                            comp_stmt = select(models.Competition).where(
                                and_(
                                    models.Competition.name == 'Serie A',
                                    models.Competition.season == season
                                )
                            )
                            competition = (await session.execute(comp_stmt)).scalar_one_or_none()

                            if not competition:
                                competition = models.Competition(
                                    name='Serie A',
                                    country='Italy',
                                    season=season,
                                    external_id=135
                                )
                                session.add(competition)
                                await session.flush()

                            # Get or create teams
                            home_team_stmt = select(models.Team).where(
                                models.Team.external_id == fixture_data.home_team_id
                            )
                            home_team = (await session.execute(home_team_stmt)).scalar_one_or_none()

                            away_team_stmt = select(models.Team).where(
                                models.Team.external_id == fixture_data.away_team_id
                            )
                            away_team = (await session.execute(away_team_stmt)).scalar_one_or_none()

                            if not home_team or not away_team:
                                logger.warning(f"Team not found for fixture {fixture_data.external_id}")
                                continue

                            # Create fixture
                            new_fixture = models.Fixture(
                                competition_id=competition.id,
                                season=season,
                                round=fixture_data.round,
                                match_date=fixture_data.match_date,
                                home_team_id=home_team.id,
                                away_team_id=away_team.id,
                                status=fixture_data.status,
                                home_score=fixture_data.home_score,
                                away_score=fixture_data.away_score,
                                external_id=fixture_data.external_id,
                                last_synced_at=datetime.utcnow()
                            )
                            session.add(new_fixture)

                        saved_count += 1

                    await session.commit()
                    logger.info(f"Saved {saved_count} fixtures to database")

                    # Log sync
                    sync_log = models.DataSyncLog(
                        provider='api_football',
                        resource_type='fixtures',
                        status='success',
                        records_synced=saved_count,
                        started_at=datetime.utcnow(),
                        completed_at=datetime.utcnow()
                    )
                    session.add(sync_log)
                    await session.commit()

                finally:
                    await orchestrator.close()

        run_async(_sync())

    except Exception as exc:
        logger.error(f"Error syncing fixtures: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def critical_pre_match_sync(self):
    """
    CRITICAL TASK: Sync data for matches starting in 60-90 minutes.

    This ensures predictions are based on fresh data (T-1h requirement).
    """
    try:
        logger.info("Starting critical T-1h pre-match sync")

        async def _sync():
            async with AsyncSessionLocal() as session:
                now = datetime.utcnow()
                window_start = now + timedelta(minutes=60)
                window_end = now + timedelta(minutes=90)

                # Find fixtures in T-1h window
                stmt = select(models.Fixture).where(
                    and_(
                        models.Fixture.match_date.between(window_start, window_end),
                        models.Fixture.status == 'scheduled'
                    )
                )
                fixtures = (await session.execute(stmt)).scalars().all()

                # Filter out fixtures that match the user's exclusion criteria
                # "elimina l'aggiornamento un'ora prima dell'inizio delle partite di serie A stagione 2025/2026 
                # a partire dalla 18 giornta che inizierà il 2 gennaio 2026"
                cutoff_date = datetime(2026, 1, 2)
                fixtures = [f for f in fixtures if f.match_date < cutoff_date]

                if not fixtures:
                    logger.info("No fixtures in T-1h window (or filtered out by policy)")
                    return

                logger.info(f"Processing {len(fixtures)} fixtures in T-1h window")

                orchestrator = DataProviderOrchestrator()

                try:
                    for fixture in fixtures:
                        try:
                            logger.info(
                                f"Syncing data for fixture {fixture.id}: "
                                f"{fixture.home_team.name} vs {fixture.away_team.name}"
                            )

                            # Sync injuries
                            await _sync_injuries_for_team(
                                session,
                                orchestrator,
                                fixture.home_team.external_id,
                                fixture.home_team_id
                            )
                            await _sync_injuries_for_team(
                                session,
                                orchestrator,
                                fixture.away_team.external_id,
                                fixture.away_team_id
                            )

                            # Update fixture last_synced_at
                            fixture.last_synced_at = datetime.utcnow()

                            await session.commit()

                            # TODO: Trigger prediction recompute
                            logger.info(f"✅ Successfully synced fixture {fixture.id}")

                        except Exception as e:
                            logger.error(f"❌ Failed to sync fixture {fixture.id}: {str(e)}")
                            await session.rollback()
                            continue

                finally:
                    await orchestrator.close()

        run_async(_sync())

    except Exception as exc:
        logger.error(f"Critical sync failed: {str(exc)}")
        # This is critical, retry aggressively
        raise self.retry(exc=exc, countdown=60)


async def _sync_injuries_for_team(session, orchestrator, external_team_id, internal_team_id):
    """Helper to sync injuries for a team"""
    try:
        injuries = await orchestrator.get_injuries_with_fallback(external_team_id)

        # Clear existing active injuries
        await session.execute(
            models.Injury.__table__.update().where(
                and_(
                    models.Injury.team_id == internal_team_id,
                    models.Injury.status == 'active'
                )
            ).values(status='recovered')
        )

        # Add new injuries
        for injury_data in injuries:
            # Get or create player
            player_stmt = select(models.Player).where(
                models.Player.external_id == injury_data.player_external_id
            )
            player = (await session.execute(player_stmt)).scalar_one_or_none()

            if not player:
                player = models.Player(
                    team_id=internal_team_id,
                    name=injury_data.player_name,
                    external_id=injury_data.player_external_id
                )
                session.add(player)
                await session.flush()

            # Create injury record
            new_injury = models.Injury(
                player_id=player.id,
                team_id=internal_team_id,
                injury_type=injury_data.injury_type,
                severity=injury_data.severity,
                expected_return_date=injury_data.expected_return,
                status='active'
            )
            session.add(new_injury)

    except Exception as e:
        logger.error(f"Error syncing injuries for team {internal_team_id}: {str(e)}")
        raise


@shared_task
def sync_all_team_stats(season: str):
    """Sync statistics for all Serie A teams"""
    try:
        logger.info(f"Syncing team stats for season {season}")

        async def _sync():
            async with AsyncSessionLocal() as session:
                # Get all teams
                stmt = select(models.Team)
                teams = (await session.execute(stmt)).scalars().all()

                orchestrator = DataProviderOrchestrator()

                try:
                    for team in teams:
                        if not team.external_id:
                            continue

                        try:
                            stats_data = await orchestrator.get_team_stats_with_fallback(
                                team.external_id,
                                season
                            )

                            # Update or create TeamStats
                            stats_stmt = select(models.TeamStats).where(
                                and_(
                                    models.TeamStats.team_id == team.id,
                                    models.TeamStats.season == season
                                )
                            )
                            existing_stats = (await session.execute(stats_stmt)).scalar_one_or_none()

                            if existing_stats:
                                existing_stats.matches_played = stats_data.matches_played
                                existing_stats.wins = stats_data.wins
                                existing_stats.draws = stats_data.draws
                                existing_stats.losses = stats_data.losses
                                existing_stats.goals_scored = stats_data.goals_scored
                                existing_stats.goals_conceded = stats_data.goals_conceded
                            else:
                                new_stats = models.TeamStats(
                                    team_id=team.id,
                                    season=season,
                                    matches_played=stats_data.matches_played,
                                    wins=stats_data.wins,
                                    draws=stats_data.draws,
                                    losses=stats_data.losses,
                                    goals_scored=stats_data.goals_scored,
                                    goals_conceded=stats_data.goals_conceded
                                )
                                session.add(new_stats)

                            await session.commit()

                        except Exception as e:
                            logger.error(f"Error syncing stats for team {team.name}: {str(e)}")
                            await session.rollback()
                            continue

                finally:
                    await orchestrator.close()

        run_async(_sync())

    except Exception as exc:
        logger.error(f"Error syncing team stats: {str(exc)}")
        raise


@shared_task(bind=True)
def sync_live_fixtures(self):
    """
    Sync currently live fixtures.
    """
    try:
        # Only run if there are potential live matches (optimization)
        # But here we rely on the provider to tell us what is live.
        # Alternatively, we could check DB first if any match is in 'live' state or scheduled around now.
        
        async def _sync():
            orchestrator = DataProviderOrchestrator()
            try:
                live_fixtures_data = await orchestrator.get_live_fixtures_with_fallback()
                
                if not live_fixtures_data:
                    return

                logger.info(f"Found {len(live_fixtures_data)} live fixtures")
                
                async with AsyncSessionLocal() as session:
                    for fixture_data in live_fixtures_data:
                        # Find existing fixture
                        stmt = select(models.Fixture).where(
                            models.Fixture.external_id == fixture_data.external_id
                        )
                        fixture = (await session.execute(stmt)).scalar_one_or_none()
                        
                        if fixture:
                            # Update details
                            fixture.status = fixture_data.status
                            fixture.home_score = fixture_data.home_score
                            fixture.away_score = fixture_data.away_score
                            fixture.last_synced_at = datetime.utcnow()
                            
                            # If we have minute/elapsed info in the future, we can add it
                            
                            logger.info(f"Updated live fixture {fixture.id}: {fixture.home_score}-{fixture.away_score}")
                    
                    await session.commit()
            
            finally:
                await orchestrator.close()

        run_async(_sync())

    except Exception as exc:
        logger.error(f"Error syncing live fixtures: {str(exc)}")
        # Don't retry aggressively for live updates, just wait for next tick
