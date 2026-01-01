"""
Celery Application Configuration
"""

from celery import Celery
from celery.schedules import crontab
from app.config import get_settings

settings = get_settings()

# Create Celery app
celery_app = Celery(
    'seriea_predictions',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.tasks.sync_tasks', 'app.tasks.prediction_tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Daily fixtures sync
    'sync-season-fixtures': {
        'task': 'app.tasks.sync_tasks.sync_season_fixtures',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
        'args': ('2025-2026',)
    },

    # Team stats sync
    'sync-team-stats': {
        'task': 'app.tasks.sync_tasks.sync_all_team_stats',
        'schedule': crontab(hour=3, minute=0),  # 3 AM daily
        'args': ('2025-2026',)
    },

    # Critical: T-1h prediction refresh (check every 30 minutes)
    'critical-pre-match-sync': {
        'task': 'app.tasks.sync_tasks.critical_pre_match_sync',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },

    # Live updates
    'sync-live-fixtures': {
        'task': 'app.tasks.sync_tasks.sync_live_fixtures',
        'schedule': crontab(minute='*'),  # Every minute
    },

    # Post-match evaluation
    'evaluate-predictions': {
        'task': 'app.tasks.prediction_tasks.evaluate_finished_matches',
        'schedule': crontab(hour='*/2'),  # Every 2 hours
    },

    # Weekly batch prediction generation
    'batch-generate-predictions': {
        'task': 'app.tasks.prediction_tasks.batch_generate_predictions',
        'schedule': crontab(hour=1, minute=0, day_of_week=1),  # Every Monday at 1 AM
        'args': ('2025-2026',)
    },
}

if __name__ == '__main__':
    celery_app.start()
