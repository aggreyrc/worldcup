"""
SofaScore provider via RapidAPI.

This provider implements SofaScore endpoints available through RapidAPI.
"""
import os
import logging
import requests
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .base import SportsDataProvider, MatchScore

logger = logging.getLogger(__name__)

STATUS_MAP = {
    "live": "live",
    "inprogress": "live",
    "in_progress": "live",
    "in-play": "live",
    "half-time": "ht",
    "ht": "ht",
    "fulltime": "ft",
    "ft": "ft",
    "finished": "ft",
    "cancelled": "cancelled",
    "canceled": "cancelled",
    "postponed": "postponed",
    "scheduled": "ns",
    "not-started": "ns",
    "ns": "ns",
}


class SofaScoreProvider(SportsDataProvider):
    def __init__(self):
        self.api_key = os.getenv("SOFASCORE_KEY")
        self.base_url = "https://sofascore.p.rapidapi.com"
        self.rapid_host = "sofascore.p.rapidapi.com"
        if not self.api_key:
            logger.warning("SOFASCORE_KEY is not configured; SofaScore requests will fail")

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.rapid_host,
        }
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            logger.warning("SofaScore request failed %s %s %s", response.status_code, url, response.text)
        except Exception as exc:
            logger.exception("SofaScore request failed for %s: %s", endpoint, exc)
        return {}

    def _status(self, status_value: Any) -> str:
        if isinstance(status_value, dict):
            status_value = status_value.get("type") or status_value.get("slug") or status_value.get("name") or ""
        if isinstance(status_value, str):
            return STATUS_MAP.get(status_value.lower(), "ns")
        return "ns"

    def _to_int(self, value: Any) -> Optional[int]:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _score(self, value: Any) -> Optional[int]:
        if isinstance(value, dict):
            return self._to_int(value.get("current") or value.get("display") or value.get("value"))
        return self._to_int(value)

    def _iso_timestamp(self, value: Any) -> str:
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(int(value), timezone.utc).isoformat().replace("+00:00", "Z")
        if isinstance(value, str):
            return value
        return ""

    def _extract_events(self, data: Any) -> List[Dict[str, Any]]:
        if isinstance(data, dict):
            for key in ("events", "data", "results", "matches"):
                if isinstance(data.get(key), list):
                    return data.get(key)
        if isinstance(data, list):
            return data
        return []

    def _map_event(self, event: Dict[str, Any]) -> MatchScore:
        home = event.get("homeTeam") or event.get("home_team") or {}
        away = event.get("awayTeam") or event.get("away_team") or {}
        tournament = event.get("tournament") or {}
        competition_id = str(tournament.get("id") or "")
        home_id = str(home.get("id") or "")
        away_id = str(away.get("id") or "")

        return MatchScore(
            match_id=str(event.get("id", "")),
            home_team=home.get("name", "") or home.get("shortName", ""),
            away_team=away.get("name", "") or away.get("shortName", ""),
            home_team_id=home_id,
            away_team_id=away_id,
            home_score=self._score(event.get("homeScore") or event.get("home_score") or event.get("scores", {}).get("home")),
            away_score=self._score(event.get("awayScore") or event.get("away_score") or event.get("scores", {}).get("away")),
            status=self._status(event.get("status") or event.get("state") or {}),
            minute=self._to_int(event.get("minute") or event.get("half") or event.get("period")),
            competition=tournament.get("name", ""),
            competition_id=competition_id,
            kickoff_utc=self._iso_timestamp(event.get("startTimestamp") or event.get("startDate") or event.get("startTime")),
            venue=(event.get("venue") or {}).get("name"),
            round=(event.get("round") or {}).get("name") or event.get("round"),
            home_logo="",
            away_logo="",
            competition_logo="",
            extra={"raw": event},
        )

    def _map_team(self, team: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": str(team.get("id", "")),
            "name": team.get("name", "") or team.get("shortName", ""),
            "code": team.get("slug", ""),
            "country": (team.get("country") or {}).get("name", "") if isinstance(team.get("country"), dict) else team.get("country", ""),
            "founded": team.get("foundationYear") or team.get("foundation_date") or None,
            "logo": team.get("logo", ""),
            "venue": {
                "name": (team.get("venue") or {}).get("name", ""),
                "city": (team.get("venue") or {}).get("city", ""),
                "capacity": (team.get("venue") or {}).get("capacity"),
                "image": (team.get("venue") or {}).get("image", ""),
            },
        }

    def _find_team(self, query: str) -> Dict[str, Any]:
        data = self._get("search", {"q": query, "type": "teams"})
        events = self._extract_events(data)
        if events:
            return events[0]
        return {}

    def get_live_scores(self, sport: str = "football") -> List[MatchScore]:
        if sport != "football":
            return []
        data = self._get("tournaments/get-live-events")
        return [self._map_event(event) for event in self._extract_events(data)]

    def get_fixtures(self, date_from: str, date_to: str, sport: str = "football") -> List[Dict[str, Any]]:
        if sport != "football":
            return []
        attempts = [
            {"from": date_from, "to": date_to},
            {"dateFrom": date_from, "dateTo": date_to},
            {"startDate": date_from, "endDate": date_to},
            {},
        ]
        events = []
        for params in attempts:
            data = self._get("tournaments/get-scheduled-events", params)
            events = self._extract_events(data)
            if events:
                break
        return [self._map_event(event).to_dict() for event in events]

    def get_fixture_detail(self, fixture_id: str) -> Dict[str, Any]:
        candidates = [
            ("matches/detail", "id"),
            ("matches/get-details", "id"),
            ("matches/detail", "matchId"),
            ("tournaments/detail", "id"),
        ]
        for endpoint, key in candidates:
            data = self._get(endpoint, {key: fixture_id})
            if not data:
                continue
            if isinstance(data, dict) and data.get("data"):
                return data["data"]
            if isinstance(data, dict) and data.get("match"):
                return data["match"]
            if isinstance(data, dict) and data.get("event"):
                return data["event"]
            if isinstance(data, dict):
                return data
        return {}

    def get_lineups(self, fixture_id: str) -> Dict[str, Any]:
        data = self._get("matches/get-lineups", {"id": fixture_id})
        if isinstance(data, dict) and data.get("data"):
            return data["data"]
        if isinstance(data, dict) and data.get("lineups"):
            return data["lineups"]
        fallback = self.get_fixture_detail(fixture_id)
        return fallback.get("lineups", {}) if isinstance(fallback, dict) else {}

    def get_standings(self, competition_id: str, season: str) -> Dict[str, Any]:
        data = self._get("tournaments/detail", {"id": competition_id})
        detail = data.get("data") if isinstance(data, dict) else data
        if not isinstance(detail, dict):
            return []
        standings = detail.get("standings") or detail.get("table") or []
        if isinstance(standings, list):
            return [
                {
                    "position": item.get("position"),
                    "team_id": str((item.get("team") or {}).get("id", "")),
                    "team_name": (item.get("team") or {}).get("name", ""),
                    "team_logo": (item.get("team") or {}).get("logo", ""),
                    "played": item.get("played", 0),
                    "won": item.get("won", 0),
                    "drawn": item.get("drawn", 0),
                    "lost": item.get("lost", 0),
                    "goals_for": item.get("goals_for", 0),
                    "goals_against": item.get("goals_against", 0),
                    "goals_diff": item.get("goal_difference", 0),
                    "points": item.get("points", 0),
                    "form": item.get("form", ""),
                    "description": item.get("description", ""),
                }
                for item in standings
            ]
        return []

    def get_team(self, team_id: str) -> Dict[str, Any]:
        data = self._get("teams/detail", {"id": team_id})
        if isinstance(data, dict) and data.get("data"):
            return self._map_team(data["data"])
        if isinstance(data, dict) and data.get("team"):
            return self._map_team(data["team"])
        match = self._find_team(team_id)
        return self._map_team(match)

    def get_team_fixtures(self, team_id: str, last: int = 5, next: int = 5) -> Dict[str, Any]:
        upcoming = self._get("tournaments/get-scheduled-events", {"teamId": team_id})
        live = self._get("tournaments/get-live-events", {"teamId": team_id})
        last_events = self._extract_events(live)[:last]
        next_events = self._extract_events(upcoming)[:next]
        return {
            "last": [self._map_event(event).to_dict() for event in last_events],
            "next": [self._map_event(event).to_dict() for event in next_events],
        }
