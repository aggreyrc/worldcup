"""
API-Football provider — compatible with Python 3.8+
With added dynamic fallback routing for SportAPI7
"""
import os
import time
import logging
import requests
from typing import Optional, List, Dict, Any
from .base import SportsDataProvider, MatchScore

logger = logging.getLogger(__name__)

STATUS_MAP = {
    "TBD": "ns",  "NS": "ns",   "1H": "live", "HT": "ht",
    "2H": "live", "ET": "live", "P":  "live", "FT": "ft",
    "AET": "ft",  "PEN": "ft",  "BT": "live", "SUSP": "postponed",
    "INT": "postponed", "PST": "postponed",    "CANC": "cancelled",
    "ABD": "abandoned"
}

class ApiFootballProvider(SportsDataProvider):
    def __init__(self):
        self.use_sofascore = os.getenv("FOOTBALL_PROVIDER") == "sofascore"
        if self.use_sofascore:
            self.api_key = os.getenv("SOFASCORE_KEY") or os.getenv("APIFOOTBALL_KEY")
            self.base_url = "https://sofascore.p.rapidapi.com/api/v1"
            self.rapid_host = "sofascore.p.rapidapi.com"
        else:
            self.api_key = os.getenv("APIFOOTBALL_KEY")
            self.use_rapidapi = os.getenv("APIFOOTBALL_USE_RAPIDAPI", "true").lower() == "true"
            if self.use_rapidapi:
                self.base_url = "https://api-football-v1.p.rapidapi.com/v3"
                self.rapid_host = "api-football-v1.p.rapidapi.com"
            else:
                self.base_url = "https://v3.football.api-sports.io"
                self.rapid_host = "v3.football.api-sports.io"

    def _get(self, endpoint, params=None):
        headers = {"x-rapidapi-key": self.api_key}
        if self.use_sofascore or getattr(self, 'use_rapidapi', True):
            headers["x-rapidapi-host"] = self.rapid_host
        else:
            headers["x-apisports-key"] = self.api_key

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
        league_logo = f"https://sofascore.p.rapidapi.com/api/v1/unique-tournament/{league_id}/image" if unique_tournament.get("id") else ""

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
                "logo": f"https://sofascore.p.rapidapi.com/api/v1/team/{home_team.get('id')}/image" if home_team.get("id") else ""
            },
            away_team={
                "id": str(away_team.get("id", "")),
                "name": away_team.get("name", ""),
                "logo": f"https://sofascore.p.rapidapi.com/api/v1/team/{away_team.get('id')}/image" if away_team.get("id") else ""
            },
            home_score=home_score,
            away_score=away_score
        )

    # ── Live/Scores ───────────────────────────────────────────
    def get_live_scores(self):
        if self.use_sportapi7:
            data = self._get("sport/football/events/live")
            return [self._map_sportapi7(f).to_dict() for f in data.get("events", [])]
        
        # Original ApiFootball implementation logic would sit below...
        return []

    # ── Standings ──────────────────────────────────────────────
    def get_standings(self, league_id, season):
        if self.use_sportapi7:
            data = self._get(f"tournament/{league_id}/season/{season}/standings/total")
            if not data or "standings" not in data:
                seasons_data = self._get(f"tournament/{league_id}/seasons")
                for s in seasons_data.get("seasons", []):
                    if str(season) in s.get("year", "") or str(season) in s.get("name", ""):
                        data = self._get(f"tournament/{league_id}/season/{s.get('id')}/standings/total")
                        break

            result = []
            standings_list = data.get("standings", [])
            if standings_list:
                for e in standings_list[0].get("rows", []):
                    team_obj = e.get("team", {})
                    tid = str(team_obj.get("id", ""))
                    result.append({
                        "position":      e.get("position"),
                        "team_id":       tid,
                        "team_name":     team_obj.get("name", ""),
                        "team_logo":     f"https://sofascore.p.rapidapi.com/api/v1/team/{tid}/image" if tid else "",
                        "played":        e.get("matches", 0),
                        "won":           e.get("wins", 0),
                        "drawn":         e.get("draws", 0),
                        "lost":          e.get("losses", 0),
                        "goals_for":     e.get("scoresFor", 0),
                        "goals_against": e.get("scoresAgainst", 0),
                        "goals_diff":    e.get("scoresFor", 0) - e.get("scoresAgainst", 0),
                        "points":        e.get("points", 0),
                        "form":          "",
                        "description":   e.get("description", ""),
                    })
            return result

        # Original Api-Football Standings Code
        data = self._get("standings", {"league": league_id, "season": season}).get("response", [])
        if not data: return []
        result = []
        for league_data in data:
            for group in league_data.get("league", {}).get("standings", []):
                result.extend([
                    {
                        "position":        e.get("rank"),
                        "team_id":         str(e.get("team", {}).get("id", "")),
                        "team_name":       e.get("team", {}).get("name", ""),
                        "team_logo":       e.get("team", {}).get("logo", ""),
                        "played":          e.get("all", {}).get("played", 0),
                        "won":             e.get("all", {}).get("win", 0),
                        "drawn":           e.get("all", {}).get("draw", 0),
                        "lost":            e.get("all", {}).get("lose", 0),
                        "goals_for":       e.get("all", {}).get("goals", {}).get("for", 0),
                        "goals_against":   e.get("all", {}).get("goals", {}).get("against", 0),
                        "goals_diff":      e.get("goalsDiff", 0),
                        "points":          e.get("points", 0),
                        "form":            e.get("form", ""),
                        "description":     e.get("description", ""),
                    }
                    for e in group
                ])
        return result

    # ── Team ──────────────────────────────────────────────────
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
                "logo": f"https://sofascore.p.rapidapi.com/api/v1/team/{team_id}/image",
                "venue": {
                    "name": venue.get("name", ""),
                    "city": city_name,
                    "capacity": venue.get("capacity"),
                    "image": f"https://sofascore.p.rapidapi.com/api/v1/venue/{venue.get('id')}/image" if venue.get("id") else "",
                },
            }

        data = self._get("teams", {"id": team_id}).get("response", [])
        if not data: return {}
        t = data[0]
        return {
            "id":      str(t.get("team", {}).get("id", "")),
            "name":    t.get("team", {}).get("name", ""),
            "code":    t.get("team", {}).get("code", ""),
            "country": t.get("team", {}).get("country", ""),
            "founded": t.get("team", {}).get("founded"),
            "logo":    t.get("team", {}).get("logo", ""),
            "venue": {
                "name":     t.get("venue", {}).get("name", ""),
                "city":     t.get("venue", {}).get("city", ""),
                "capacity": t.get("venue", {}).get("capacity"),
                "image":    t.get("venue", {}).get("image", ""),
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

        last_data = self._get("fixtures", {"team": team_id, "last": last})
        next_data = self._get("fixtures", {"team": team_id, "next": next})
        return {
            "last": [self._map(f).to_dict() for f in (last_data.get("response") or [])],
            "next": [self._map(f).to_dict() for f in (next_data.get("response") or [])]
        }