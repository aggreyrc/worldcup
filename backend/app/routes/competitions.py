"""
Competition routes.

GET /api/v1/standings/<competition_id>   — league table / group standings
GET /api/v1/competition/<slug>           — competition metadata
"""
import json
import os
import logging

from flask import Blueprint, jsonify, request
from app import cache, limiter
from app.sports_data.factory import get_provider

logger = logging.getLogger(__name__)
bp = Blueprint("competitions", __name__, url_prefix="/api/v1")


def _redis():
    import redis as redis_lib
    return redis_lib.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)


# Featured competitions with their API-Football IDs
FEATURED_COMPETITIONS = [
    {"id": "1", "name": "World Cup", "slug": "world-cup", "country": "World", "season": "2026"},
    {"id": "2", "name": "Champions League", "slug": "champions-league", "country": "Europe", "season": "2025"},
    {"id": "39", "name": "Premier League", "slug": "premier-league", "country": "England", "season": "2025"},
    {"id": "140", "name": "La Liga", "slug": "la-liga", "country": "Spain", "season": "2025"},
    {"id": "78", "name": "Bundesliga", "slug": "bundesliga", "country": "Germany", "season": "2025"},
    {"id": "135", "name": "Serie A", "slug": "serie-a", "country": "Italy", "season": "2025"},
    {"id": "61", "name": "Ligue 1", "slug": "ligue-1", "country": "France", "season": "2025"},
    {"id": "197", "name": "Africa Cup of Nations", "slug": "afcon", "country": "Africa", "season": "2025"},
]


@bp.get("/competitions/featured")
@cache.cached(timeout=3600, key_prefix="featured_competitions")
def featured_competitions():
    """List of featured competitions for the homepage."""
    return jsonify({"data": FEATURED_COMPETITIONS})


@bp.get("/standings/<competition_id>")
@limiter.limit("30 per minute")
def standings(competition_id: str):
    """
    League table for a competition + season.
    Cached 5 minutes — only changes after a match finishes.
    """
    sport = request.args.get("sport", "football")
    season = request.args.get("season", "2025")

    r = _redis()
    cache_key = f"standings:{sport}:{competition_id}:{season}"
    raw = r.get(cache_key)
    if raw:
        return jsonify({"data": json.loads(raw), "source": "cache"})

    try:
        provider = get_provider(sport)
        data = provider.get_standings(competition_id, season)
        r.setex(cache_key, 300, json.dumps(data))
        return jsonify({"data": data, "source": "live"})
    except Exception as exc:
        logger.error(f"Standings error ({competition_id}): {exc}")
        return jsonify({"error": "Standings unavailable"}), 503
