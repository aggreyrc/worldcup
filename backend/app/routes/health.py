"""Health check — used by Docker, ECS, and load balancer."""
import os
from flask import Blueprint, jsonify

bp = Blueprint("health", __name__)


@bp.get("/health")
def health():
    checks = {"api": "ok"}

    # Check Redis
    try:
        import redis as redis_lib
        r = redis_lib.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"))
        r.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {e}"

    # Check DB
    try:
        from app import db
        db.session.execute(db.text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"

    status_code = 200 if all(v == "ok" for v in checks.values()) else 503
    return jsonify({"status": "ok" if status_code == 200 else "degraded", "checks": checks}), status_code


@bp.get("/api/v1/sports")
def sports_list():
    """Available sports (static, extensible)."""
    return jsonify({
        "data": [
            {"slug": "football", "name": "Football", "active": True},
            {"slug": "basketball", "name": "Basketball", "active": False},
            {"slug": "tennis", "name": "Tennis", "active": False},
            {"slug": "cricket", "name": "Cricket", "active": False},
        ]
    })
