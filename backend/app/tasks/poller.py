"""
Celery background tasks — poll sports data providers and warm Redis cache.
Flask routes NEVER call the provider directly on a user request.
Celery polls on a schedule; Flask always reads from Redis.
"""
import os
import json
import logging
from datetime import datetime, timedelta, timezone

from app.celery_app import celery_app
from app.sports_data.factory import get_provider

logger = logging.getLogger(__name__)

REDIS_TTL_LIVE     = 120   # 4× the 15s poll interval
REDIS_TTL_FIXTURES = 600   # 10 min
REDIS_TTL_STANDINGS = 600


def get_redis():
    """Return a raw Redis client using the correct container URL."""
    import redis as redis_lib
    url = (os.environ.get("REDIS_URL") or "redis://redis:6379/0")
    return redis_lib.from_url(url, decode_responses=True)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    name="app.tasks.poller.poll_live_scores",
)
def poll_live_scores(self, sport: str = "football"):
    """
    Polls the provider for live scores and writes to Redis.
    Runs every CACHE_LIVE_SCORES_TTL seconds (default 15s) via Celery Beat.
    """
    r = get_redis()
    try:
        provider = get_provider(sport)
        scores = provider.get_live_scores(sport)
        serialised = [s.to_dict() for s in scores]

        cache_key = f"live_scores:{sport}"
        r.setex(cache_key, REDIS_TTL_LIVE, json.dumps(serialised))
        r.setex(f"live_count:{sport}", REDIS_TTL_LIVE, str(len(serialised)))

        logger.info(f"[Poller] Cached {len(serialised)} live {sport} matches")
        return {"count": len(serialised), "sport": sport}

    except Exception as exc:
        logger.warning(f"[Poller] Live scores poll failed ({sport}): {exc}")
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=60,
    name="app.tasks.poller.poll_fixtures",
)
def poll_fixtures(self, sport: str = "football"):
    """
    Polls upcoming fixtures across all featured leagues.
    Runs every 5 minutes — conserves free-tier API quota (100 req/day).
    """
    r = get_redis()
    try:
        provider = get_provider(sport)
        now = datetime.now(timezone.utc)
        date_from = now.date().isoformat()
        date_to   = (now + timedelta(days=3)).date().isoformat()

        fixtures = provider.get_fixtures(date_from, date_to, sport)
        cache_key = f"fixtures:{sport}:{date_from}"
        r.setex(cache_key, REDIS_TTL_FIXTURES, json.dumps(fixtures))

        logger.info(f"[Poller] Cached {len(fixtures)} {sport} fixtures")
        return {"count": len(fixtures), "sport": sport}

    except Exception as exc:
        logger.warning(f"[Poller] Fixtures poll failed ({sport}): {exc}")
        raise self.retry(exc=exc)
