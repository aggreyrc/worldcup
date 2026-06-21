"""
LiveScore Platform — Flask Application Factory
No Celery dependency — uses Flask-Caching with Redis backend directly.
Works on Render's free tier (web service only, no background worker needed).
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
limiter = Limiter(key_func=get_remote_address, default_limits=["300 per minute"])


def create_app(config_name=None):
    app = Flask(__name__)

    env = config_name or os.environ.get("FLASK_ENV", "development")

    database_url = os.environ.get("DATABASE_URL", "postgresql://livescore:livescore@localhost:5433/livescore")
    # Render gives postgres:// URLs but SQLAlchemy needs postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-change-in-prod"),
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping": True, "pool_size": 5},
        CACHE_TYPE="RedisCache",
        CACHE_REDIS_URL=redis_url,
        CACHE_DEFAULT_TIMEOUT=60,
        RATELIMIT_STORAGE_URI=redis_url,
        DEBUG=env == "development",
    )

    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    limiter.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    from .routes.scores import bp as scores_bp
    from .routes.fixtures import bp as fixtures_bp
    from .routes.competitions import bp as competitions_bp
    from .routes.teams import bp as teams_bp
    from .routes.search import bp as search_bp
    from .routes.health import bp as health_bp

    app.register_blueprint(scores_bp)
    app.register_blueprint(fixtures_bp)
    app.register_blueprint(competitions_bp)
    app.register_blueprint(teams_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(health_bp)

    with app.app_context():
        from . import models  # noqa: F401

    return app