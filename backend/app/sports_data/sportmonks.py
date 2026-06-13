"""
Sportmonks Football Pro via RapidAPI
With added dynamic fallback routing for SportAPI7
"""
import os
import time
import logging
import requests
from typing import Optional, List, Dict, Any
from .base import SportsDataProvider, MatchScore

logger = logging.getLogger(__name__)

STATE_MAP = {
    1:  "ns",      2:  "live",  3:  "live",  4:  "ht",
    5:  "live",    6:  "live",  7:  "live",  8:  "live",
    9:  "ft",      10: "ft",    11: "postponed", 12: "cancelled",
    13: "abandoned", 14: "live", 15: "live",  16: "ft",
    17: "ft",      18: "ft",    31: "ns",
}

class SportMonksProvider(SportsDataProvider):
    def __init__(self):
        self.use_sportapi7 = os.getenv("FOOTBALL_PROVIDER") == "sportapi7"
        if self.use_sportapi7:
            self.api_key = os.getenv("SOFASCORE_KEY") or os.getenv("SPORTMONKS_KEY")
            self.base_url = "https://sofascore.p.rapidapi.com/api/v1"
            self.rapid_host = "sofascore.p.rapidapi.com"
        else:
            self.api_key = os.getenv("SPORTMONKS_KEY")
            self.base_url = "https://sportmonks-football-pro.p.rapidapi.com/api/v3/football"
            self.rapid_host = "sportmonks-football-pro.p.rapidapi.com"

    def _get(self, endpoint, params=None):
        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.rapid_host
        }
        url = f"{self.base_url}/{endpoint}"
        try:
            res = requests.get(url, headers=headers, params=params)
            if res.status_code == 200:
                return res.json()
        except Exception as e:
            logger.error(f"Request failed for {endpoint}: {e}")
        return {}

    def _map_sportapi7(self, f):
        status_obj = f.get("status", {})
        status_type = status_obj.get("type", "")
        status_code = status_obj.get("code", 0)

        if status_code == 0: status = "ns"
        elif status_code == 60: status = "ht"
        elif status_code == 100: status = "ft"
        elif status_type == "finished": status = "ft"
        elif status_type == "inprogress": status = "live"
        elif status_type == "postponed": status = "postponed"
        elif status_type == "canceled": status = "cancelled"
        else: status = "ns"

        home_team = f.get("homeTeam", {})
        away_team = f.get("awayTeam", {})
        home_score = f.get("homeScore", {}).get("current")
        away_score = f.get("awayScore", {}).get("current")

        tournament = f.get("tournament", {})
        unique_tournament = tournament.get("uniqueTournament", {})
        league_id = str(unique_tournament.get("id") or tournament.get("id") or "")
        league_name = unique_tournament.get("name") or tournament.get("name") or ""
        league_logo = f"https://sportapi7.p.rapidapi.com/api/v1/unique-tournament/{league_id}/image" if unique_tournament.get("id") else ""

        return MatchScore(
            id=str(f.get("id", "")),
            league_id=league_id,
            league_name=league_name,
            league_logo=league_logo,
            status=status,
            minute=None,
            timestamp=f.get("startTimestamp"),
            home_team={
                "id": str(home_team.get("id", "")),
                "name": home_team.get("name", ""),
                "logo": f"https://sportapi7.p.rapidapi.com/api/v1/team/{home_team.get('id')}/image" if home_team.get("id") else ""
            },
            away_team={
                "id": str(away_team.get("id", "")),
                "name": away_team.get("name", ""),
                "logo": f"https://sportapi7.p.rapidapi.com/api/v1/team/{away_team.get('id')}/image" if away_team.get("id") else ""
            },
            home_score=home_score,
            away_score=away_score
        )

    def get_team(self, team_id):
        if self.use_sportapi7:
            data = self._get(f"team/{team_id}")
            t = data.get("team", {})
            if not t: return {}
            venue = t.get("venue", {})
            city_obj = venue.get("city", {})
            city_name = city_obj.get("name", "") if isinstance(city_obj, dict) else city_obj
            
            founded_year = None
            if t.get("foundationDateTimestamp"):
                founded_year = time.gmtime(t.get("foundationDateTimestamp")).tm_year

            return {
                "id": str(t.get("id", "")),
                "name": t.get("name", ""),
                "code": t.get("nameCode", ""),
                "country": t.get("category", {}).get("name", ""),
                "founded": founded_year,
                "logo": f"https://sportapi7.p.rapidapi.com/api/v1/team/{team_id}/image",
                "venue": {
                    "name": venue.get("name", ""),
                    "city": city_name,
                    "capacity": venue.get("capacity"),
                    "image": f"https://sportapi7.p.rapidapi.com/api/v1/venue/{venue.get('id')}/image" if venue.get("id") else "",
                },
            }

        data = self._get("teams/{}".format(team_id), {"include": "venue;country"})
        t    = data.get("data") or {}
        if not t: return {}
        venue   = t.get("venue") or {}
        country = t.get("country") or {}
        return {
            "id": str(t.get("id", "")), "name": t.get("name", ""),
            "code": t.get("short_code", ""), "country": country.get("name", ""),
            "founded": t.get("founded"), "logo": t.get("image_path", ""),
            "venue": {
                "name": venue.get("name", ""), "city": venue.get("city", ""),
                "capacity": venue.get("capacity"), "image": venue.get("image_path", ""),
            },
        }

    def get_team_fixtures(self, team_id, last=5, next=5):
        if self.use_sportapi7:
            last_data = self._get(f"team/{team_id}/events/last/0")
            next_data = self._get(f"team/{team_id}/events/next/0")
            return {
                "last": [self._map_sportapi7(f).to_dict() for f in last_data.get("events", [])[:last]],
                "next": [self._map_sportapi7(f).to_dict() for f in next_data.get("events", [])[:next]]
            }

        try:
            last_data = self._get("fixtures", {
                "filter[team_id]": team_id,
                "include": "participants;state;scores;league",
                "per_page": last, "sort": "-starting_at",
            })
            next_data = self._get("fixtures/upcoming/teams/{}".format(team_id),
                                  {"include": "participants;state;scores;league", "per_page": next})
            return {
                "last": [self._map(f).to_dict() for f in (last_data.get("data") or [])],
                "next": [self._map(f).to_dict() for f in (next_data.get("data") or [])]
            }
        except Exception:
            return {"last": [], "next": []}