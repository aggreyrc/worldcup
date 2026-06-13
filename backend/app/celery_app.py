"""
Celery application — background task queue for polling sports data providers.
"""
import os
from celery import Celery


def make_celery():
    # Always prefer explicit vars; fall back to redis service name (not localhost)
    broker  = (os.environ.get("CELERY_BROKER_URL")
               or os.environ.get("REDIS_URL")
               or "redis://redis:6379/0")
    backend = (os.environ.get("CELERY_RESULT_BACKEND")
               or os.environ.get("REDIS_URL", "redis://redis:6379/0").replace("/0", "/1"))

    celery = Celery(
        "livescore",
        broker=broker,
        backend=backend,
        include=["app.tasks.poller"],
    )

    celery.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
        beat_schedule={
            "poll-live-scores": {
                "task": "app.tasks.poller.poll_live_scores",
                "schedule": float(os.environ.get("CACHE_LIVE_SCORES_TTL", 15)),
                "args": ("football",),
            },
            "poll-todays-fixtures": {
                "task": "app.tasks.poller.poll_fixtures",
                "schedule": 300.0,   # every 5 min — free tier has 100 req/day limit
            },
        },
        task_acks_late=True,
        worker_prefetch_multiplier=1,
    )

    return celery


celery_app = make_celery()
