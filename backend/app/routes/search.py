"""Search route — basic name-matching on featured competitions."""
import logging
from flask import Blueprint, jsonify, request
from app import limiter

logger = logging.getLogger(__name__)
bp = Blueprint("search", __name__, url_prefix="/api/v1")

# In production, replace this with an Elasticsearch query
SEARCHABLE_COMPETITIONS = [
    {"type": "competition", "id": "39",  "name": "Premier League",     "country": "England"},
    {"type": "competition", "id": "140", "name": "La Liga",            "country": "Spain"},
    {"type": "competition", "id": "78",  "name": "Bundesliga",         "country": "Germany"},
    {"type": "competition", "id": "135", "name": "Serie A",            "country": "Italy"},
    {"type": "competition", "id": "61",  "name": "Ligue 1",            "country": "France"},
    {"type": "competition", "id": "2",   "name": "Champions League",   "country": "Europe"},
    {"type": "competition", "id": "1",   "name": "World Cup",          "country": "World"},
    {"type": "competition", "id": "197", "name": "AFCON",              "country": "Africa"},
]


@bp.get("/search")
@limiter.limit("30 per minute")
def search():
    q = request.args.get("q", "").lower().strip()
    if not q or len(q) < 2:
        return jsonify({"data": []})

    results = [
        item for item in SEARCHABLE_COMPETITIONS
        if q in item["name"].lower() or q in item["country"].lower()
    ][:10]

    return jsonify({"data": results, "query": q})
