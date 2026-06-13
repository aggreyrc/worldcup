"""
Live Scores API routes.

GET  /api/v1/scores/live              — snapshot (Redis, 15s TTL)
GET  /api/v1/scores/live/stream       — SSE stream (browser keeps connection open)
GET  /api/v1/scores/live/count        — match count (monitoring / header badge)
"""
import json
import time
import logging
import os

from flask import Blueprint, jsonify, Response, stream_with_context, request
from app import cache, limiter
from app.sports_data.factory import get_provider
from typing import List, Tuple

logger = logging.getLogger(__name__)
bp = Blueprint("scores", __name__, url_prefix="/api/v1")

LIVE_CACHE_KEY_TEMPLATE = "live_scores:{sport}"
FALLBACK_TTL = 300   # Keep fallback value for 5 minutes


def _get_live_from_cache(sport: str) -> Tuple[List, str]:
    """Read live scores from Redis. Returns (data, source_label)."""
    import redis as redis_lib
    r = redis_lib.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)
    raw = r.get(f"live_scores:{sport}")
    if raw:
        return json.loads(raw), "cache"
    return [], "empty"


@bp.get("/scores/live")
@limiter.limit("120 per minute")
def live_scores():
    """
    Returns all currently live matches.
    Source: Redis (pre-populated by Celery poller).
    Falls back to direct provider call if Redis is empty.
    """
    sport = request.args.get("sport", "football")
    scores, source = _get_live_from_cache(sport)

    if not scores:
        # Cold start or cache miss — call provider directly (once)
        try:
            provider = get_provider(sport)
            raw = provider.get_live_scores(sport)
            scores = [s.to_dict() for s in raw]
            source = "live"
        except Exception as exc:
            logger.error(f"Direct provider call failed: {exc}")
            return jsonify({"error": "Live data temporarily unavailable", "data": [], "source": "error"}), 503

    return jsonify({
        "data": scores,
        "count": len(scores),
        "source": source,
        "sport": sport,
    })


@bp.get("/scores/live/stream")
@limiter.limit("10 per minute")
def live_stream():
    """
    Server-Sent Events endpoint.
    Browser connects once and receives updates every 15 seconds.
    Automatically falls back to last known data if cache is empty.
    """
    sport = request.args.get("sport", "football")
    interval = int(os.environ.get("CACHE_LIVE_SCORES_TTL", 15))

    def generate():
        while True:
            try:
                scores, source = _get_live_from_cache(sport)
                payload = json.dumps({
                    "data": scores,
                    "count": len(scores),
                    "source": source,
                    "sport": sport,
                    "ts": int(time.time()),
                })
                yield f"data: {payload}\n\n"
            except Exception as exc:
                logger.warning(f"SSE generation error: {exc}")
                yield f"data: {json.dumps({'error': str(exc)})}\n\n"
            time.sleep(interval)

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",     # Disable Nginx buffering for SSE
            "Access-Control-Allow-Origin": "*",
        },
    )


@bp.get("/scores/live/count")
@cache.cached(timeout=15, key_prefix=lambda: f"live_count_{request.args.get('sport','football')}")
def live_count():
    """Quick count endpoint for navbar badge (highly cacheable)."""
    sport = request.args.get("sport", "football")
    scores, _ = _get_live_from_cache(sport)
    return jsonify({"count": len(scores), "sport": sport})
