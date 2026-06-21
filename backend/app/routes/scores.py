"""
Live Scores API routes.
No Celery — fetches directly from provider with Flask-Caching (Redis) TTL.
This works on Render's free web-service-only tier.

GET  /api/v1/scores/live              — snapshot (cached 15s)
GET  /api/v1/scores/live/stream       — SSE stream (polls provider every 15s)
GET  /api/v1/scores/live/count        — match count for navbar badge
"""
import json
import time
import logging

from flask import Blueprint, jsonify, Response, stream_with_context, request
from app import cache, limiter
from app.sports_data.factory import get_provider

logger = logging.getLogger(__name__)
bp = Blueprint("scores", __name__, url_prefix="/api/v1")


def _fetch_live(sport):
    """Fetch live scores from provider — cached by Flask-Caching decorator on caller."""
    try:
        provider = get_provider(sport)
        raw = provider.get_live_scores(sport)
        return [s.to_dict() for s in raw], "live"
    except Exception as exc:
        logger.error("Live scores fetch failed: {}".format(exc))
        return [], "unavailable"


@bp.get("/scores/live")
@limiter.limit("120 per minute")
@cache.cached(timeout=15, query_string=True)
def live_scores():
    sport = request.args.get("sport", "football")
    scores, source = _fetch_live(sport)
    return jsonify({
        "data":   scores,
        "count":  len(scores),
        "source": source,
        "sport":  sport,
    })


@bp.get("/scores/live/stream")
@limiter.limit("10 per minute")
def live_stream():
    """SSE — polls provider every 15s and pushes to client."""
    sport = request.args.get("sport", "football")

    def generate():
        while True:
            scores, source = _fetch_live(sport)
            payload = json.dumps({
                "data":   scores,
                "count":  len(scores),
                "source": source,
                "sport":  sport,
                "ts":     int(time.time()),
            })
            yield "data: {}\n\n".format(payload)
            time.sleep(15)

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        },
    )


@bp.get("/scores/live/count")
@cache.cached(timeout=15, query_string=True)
def live_count():
    sport = request.args.get("sport", "football")
    scores, _ = _fetch_live(sport)
    return jsonify({"count": len(scores), "sport": sport})