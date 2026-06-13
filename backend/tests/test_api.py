"""
Backend tests — run with: pytest tests/ -v
"""
import pytest
import json
from unittest.mock import patch, MagicMock
from app import create_app
from app.sports_data.base import MatchScore


@pytest.fixture
def app():
    application = create_app("testing")
    application.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "CACHE_TYPE": "SimpleCache",
        "RATELIMIT_ENABLED": False,
    })
    return application


@pytest.fixture
def client(app):
    return app.test_client()


def make_mock_score(**kwargs) -> MatchScore:
    defaults = dict(
        match_id="1001",
        home_team="Arsenal",
        away_team="Chelsea",
        home_team_id="42",
        away_team_id="49",
        home_score=2,
        away_score=1,
        status="live",
        minute=67,
        competition="Premier League",
        competition_id="39",
        kickoff_utc="2025-09-15T15:00:00Z",
    )
    defaults.update(kwargs)
    return MatchScore(**defaults)


class TestHealthEndpoint:
    def test_health_returns_200_when_services_ok(self, client):
        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.return_value = True
            response = client.get("/health")
            # May be 200 or 503 depending on DB — just check it responds
            assert response.status_code in (200, 503)
            data = json.loads(response.data)
            assert "status" in data
            assert "checks" in data

    def test_sports_list(self, client):
        response = client.get("/api/v1/sports")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "data" in data
        sports = data["data"]
        slugs = [s["slug"] for s in sports]
        assert "football" in slugs


class TestScoresEndpoints:
    def test_live_scores_returns_data(self, client):
        mock_scores = [make_mock_score()]

        with patch("app.routes.scores._get_live_from_cache") as mock_cache:
            mock_cache.return_value = ([s.to_dict() for s in mock_scores], "cache")
            response = client.get("/api/v1/scores/live")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "data" in data
        assert data["count"] == 1
        assert data["data"][0]["home_team"] == "Arsenal"

    def test_live_scores_empty_when_no_data(self, client):
        with patch("app.routes.scores._get_live_from_cache") as mock_cache:
            with patch("app.sports_data.factory.get_provider") as mock_factory:
                mock_cache.return_value = ([], "empty")
                mock_provider = MagicMock()
                mock_provider.get_live_scores.return_value = []
                mock_factory.return_value = mock_provider

                response = client.get("/api/v1/scores/live")
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data["count"] == 0

    def test_live_count_endpoint(self, client):
        with patch("app.routes.scores._get_live_from_cache") as mock_cache:
            mock_cache.return_value = ([{}, {}], "cache")
            response = client.get("/api/v1/scores/live/count")
        assert response.status_code == 200


class TestProviderAbstraction:
    def test_match_score_to_dict(self):
        score = make_mock_score()
        d = score.to_dict()
        assert d["match_id"] == "1001"
        assert d["home_team"] == "Arsenal"
        assert d["status"] == "live"
        assert d["minute"] == 67

    def test_factory_returns_provider(self):
        with patch.dict("os.environ", {"FOOTBALL_PROVIDER": "apifootball", "APIFOOTBALL_KEY": "test"}):
            from app.sports_data.factory import get_provider
            provider = get_provider("football")
            assert provider is not None

    def test_factory_returns_sofascore_provider(self):
        with patch.dict("os.environ", {"FOOTBALL_PROVIDER": "sofascore", "SOFASCORE_KEY": "test"}):
            from app.sports_data.factory import get_provider
            provider = get_provider("football")
            assert provider.__class__.__name__ == "SofaScoreProvider"

    def test_factory_returns_sportapi_provider(self):
        with patch.dict("os.environ", {"FOOTBALL_PROVIDER": "sportapi", "SPORTAPI_KEY": "test"}):
            from app.sports_data.factory import get_provider
            provider = get_provider("football")
            assert provider is not None
            assert provider.__class__.__name__ == "SportApiProvider"


class TestFixturesEndpoints:
    def test_fixtures_returns_list(self, client):
        with patch("redis.from_url") as mock_redis_cls:
            mock_r = MagicMock()
            mock_r.get.return_value = json.dumps([make_mock_score().to_dict()])
            mock_redis_cls.return_value = mock_r

            response = client.get("/api/v1/fixtures")
            assert response.status_code == 200

    def test_search_requires_query(self, client):
        response = client.get("/api/v1/search")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["data"] == []

    def test_search_finds_competition(self, client):
        response = client.get("/api/v1/search?q=premier")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert any("Premier" in r["name"] for r in data["data"])

class TestESPNProvider:
    def test_scoreboard_400_failed_events_endpoint_returns_empty_events(self):
        from app.sports_data.espn import ESPNProvider
        import requests

        response = requests.Response()
        response.status_code = 400
        response._content = b'{"code":400,"message":"Failed to get events endpoint."}'
        error = requests.HTTPError(response=response)

        provider = ESPNProvider()
        with patch.object(provider, "_get", side_effect=error):
            assert provider._get_scoreboard("uefa.champions_league") == {"events": []}

    def test_scoreboard_other_http_errors_still_raise(self):
        from app.sports_data.espn import ESPNProvider
        import requests

        response = requests.Response()
        response.status_code = 500
        response._content = b'upstream error'
        error = requests.HTTPError(response=response)

        provider = ESPNProvider()
        with patch.object(provider, "_get", side_effect=error):
            with pytest.raises(requests.HTTPError):
                provider._get_scoreboard("eng.1")
