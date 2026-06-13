"""
Fixtures and match detail routes.

GET /api/v1/fixtures               — upcoming fixtures (date window)
GET /api/v1/match/<id>             — full match detail + events + stats
GET /api/v1/match/<id>/lineups     — starting XIs
"""
import json
import os
import logging
from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request
from app import cache, limiter
from app.sports_data.factory import get_provider

logger = logging.getLogger(__name__)
bp = Blueprint("fixtures", __name__, url_prefix="/api/v1")


def _redis():
    import redis as redis_lib
    return redis_lib.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)


@bp.get("/fixtures")
@limiter.limit("60 per minute")
def fixtures():
    """
    Returns fixtures for a date range (default: today → +3 days).
    Checks Redis first (pre-populated by Celery), falls back to direct call.
    """
    sport = request.args.get("sport", "football")
    date_from = request.args.get("from") or datetime.now(timezone.utc).date().isoformat()
    date_to = request.args.get("to") or (datetime.now(timezone.utc) + timedelta(days=3)).date().isoformat()

    # Try Redis first
    r = _redis()
    cache_key = f"fixtures:{sport}:{date_from}"
    raw = r.get(cache_key)
    if raw:
        return jsonify({"data": json.loads(raw), "source": "cache"})

    # Direct call
    try:
        provider = get_provider(sport)
        data = provider.get_fixtures(date_from, date_to, sport)
        r.setex(cache_key, 120, json.dumps(data))
        return jsonify({"data": data, "source": "live"})
    except Exception as exc:
        logger.error(f"Fixtures error: {exc}")
        return jsonify({"error": "Fixtures unavailable", "data": []}), 503


@bp.get("/match/<fixture_id>")
@limiter.limit("60 per minute")
def match_detail(fixture_id: str):
    """Full match detail: score, events, statistics."""
    sport = request.args.get("sport", "football")

    r = _redis()
    cache_key = f"match_detail:{sport}:{fixture_id}"
    raw = r.get(cache_key)
    if raw:
        return jsonify({"data": json.loads(raw), "source": "cache"})

    try:
        provider = get_provider(sport)
        detail = provider.get_fixture_detail(fixture_id)

        # Cache duration depends on match status
        ttl = 20 if detail.get("status") == "live" else 300
        r.setex(cache_key, ttl, json.dumps(detail))

        return jsonify({"data": detail, "source": "live"})
    except Exception as exc:
        logger.error(f"Match detail error ({fixture_id}): {exc}")
        return jsonify({"error": "Match detail unavailable"}), 503


@bp.get("/match/<fixture_id>/lineups")
@limiter.limit("30 per minute")
def match_lineups(fixture_id: str):
    """Starting XIs — released ~1hr before kickoff, rarely changes."""
    sport = request.args.get("sport", "football")

    r = _redis()
    cache_key = f"lineups:{sport}:{fixture_id}"
    raw = r.get(cache_key)
    if raw:
        return jsonify({"data": json.loads(raw), "source": "cache"})

    try:
        provider = get_provider(sport)
        lineups = provider.get_lineups(fixture_id)
        r.setex(cache_key, 600, json.dumps(lineups))   # 10 min TTL
        return jsonify({"data": lineups, "source": "live"})
    except Exception as exc:
        logger.error(f"Lineups error ({fixture_id}): {exc}")
        return jsonify({"error": "Lineups unavailable", "data": {}}), 503
