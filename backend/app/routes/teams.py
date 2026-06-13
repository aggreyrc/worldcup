"""
Team routes.

GET /api/v1/team/<team_id>            — team profile + venue
GET /api/v1/team/<team_id>/fixtures   — recent + upcoming fixtures
"""
import json
import os
import logging

from flask import Blueprint, jsonify, request
from app import cache, limiter
from app.sports_data.factory import get_provider

logger = logging.getLogger(__name__)
bp = Blueprint("teams", __name__, url_prefix="/api/v1")


def _redis():
    import redis as redis_lib
    return redis_lib.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)


@bp.get("/team/<team_id>")
@limiter.limit("30 per minute")
def team_profile(team_id: str):
    sport = request.args.get("sport", "football")

    r = _redis()
    cache_key = f"team:{sport}:{team_id}"
    raw = r.get(cache_key)
    if raw:
        return jsonify({"data": json.loads(raw), "source": "cache"})

    try:
        provider = get_provider(sport)
        data = provider.get_team(team_id)
        r.setex(cache_key, 86400, json.dumps(data))   # 24h TTL — team data rarely changes
        return jsonify({"data": data, "source": "live"})
    except Exception as exc:
        logger.error(f"Team error ({team_id}): {exc}")
        return jsonify({"error": "Team data unavailable"}), 503


@bp.get("/team/<team_id>/fixtures")
@limiter.limit("30 per minute")
def team_fixtures(team_id: str):
    sport = request.args.get("sport", "football")
    last = int(request.args.get("last", 5))
    next_ = int(request.args.get("next", 5))

    r = _redis()
    cache_key = f"team_fixtures:{sport}:{team_id}:{last}:{next_}"
    raw = r.get(cache_key)
    if raw:
        return jsonify({"data": json.loads(raw), "source": "cache"})

    try:
        provider = get_provider(sport)
        data = provider.get_team_fixtures(team_id, last, next_)
        r.setex(cache_key, 300, json.dumps(data))
        return jsonify({"data": data, "source": "live"})
    except Exception as exc:
        logger.error(f"Team fixtures error ({team_id}): {exc}")
        return jsonify({"error": "Team fixtures unavailable"}), 503
