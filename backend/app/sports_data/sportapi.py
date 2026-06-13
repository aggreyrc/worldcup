"""
SportAPI provider via RapidAPI — https://rapidapi.com/rapidsportapi/api/sportapi7

Base URL: https://sportapi7.p.rapidapi.com
Auth: x-rapidapi-key header — works from any IP including Docker.

Key endpoints used:
  GET /api/v1/sport/football/events/live              — live scores
  GET /api/v1/sport/football/scheduled-events/{date}  — fixtures by date
  GET /api/v1/event/{id}/incidents                    — goals, cards, subs
  GET /api/v1/event/{id}/lineups                      — starting XIs
  GET /api/v1/event/{id}/statistics                   — match stats
  GET /api/v1/unique-tournament/{id}/season/{sid}/standings/total — league table
  GET /api/v1/team/{id}                               — team profile
  GET /api/v1/team/{id}/events/next/0                 — upcoming fixtures
  GET /api/v1/team/{id}/events/last/0                 — recent results

Compatible with Python 3.8+
"""
import os
import logging
import requests
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from .base import SportsDataProvider, MatchScore

logger = logging.getLogger(__name__)

BASE_URL   = "https://sportapi7.p.rapidapi.com"
RAPID_HOST = "sportapi7.p.rapidapi.com"

# SportAPI status codes → our normalised status strings
STATUS_MAP = {
    # Common status types SportAPI uses
    "inprogress":   "live",
    "live":         "live",
    "halftime":     "ht",
    "finished":     "ft",
    "notstarted":   "ns",
    "postponed":    "postponed",
    "cancelled":    "cancelled",
    "interrupted":  "postponed",
    "abandoned":    "cancelled",
    "coverage":     "ns",
    "awaitingextratime": "ht",
    "extratime":    "live",
    "penalties":    "live",
    "awaitingpenalties": "ht",
    "penaltiescompleted": "ft",
}

# Featured tournament (unique tournament) IDs in SportAPI
# Find these via /api/v1/sport/football/categories
FEATURED_TOURNAMENTS = [
    {"id": 17,   "season_id": 61627, "name": "Premier League"},
    {"id": 8,    "season_id": 61644, "name": "La Liga"},
    {"id": 35,   "season_id": 61619, "name": "Bundesliga"},
    {"id": 23,   "season_id": 61620, "name": "Serie A"},
    {"id": 34,   "season_id": 61596, "name": "Ligue 1"},
    {"id": 7,    "season_id": 61643, "name": "Champions League"},
    {"id": 679,  "season_id": 57478, "name": "World Cup"},
]


class SportApiProvider(SportsDataProvider):

    def __init__(self):
        self.key = os.environ.get("RAPIDAPI_KEY", "").strip()
        if not self.key:
            logger.warning(
                "RAPIDAPI_KEY not set. "
                "Copy your key from https://rapidapi.com/rapidsportapi/api/sportapi7"
            )
        else:
            logger.info("SportAPI provider ready")

    def _get(self, path, params=None):
        """GET request to SportAPI via RapidAPI."""
        url = "{}/{}".format(BASE_URL, path.lstrip("/"))
        headers = {
            "x-rapidapi-host": RAPID_HOST,
            "x-rapidapi-key":  self.key,
        }
        try:
            resp = requests.get(url, headers=headers, params=params or {}, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.Timeout:
            logger.error("Timeout on {}".format(path))
            raise
        except requests.HTTPError as e:
            logger.error("HTTP {} on {}: {}".format(
                e.response.status_code, path, e.response.text[:300]))
            raise
        except requests.RequestException as e:
            logger.error("Request error on {}: {}".format(path, e))
            raise

    def _parse_status(self, event):
        """Extract normalised status from a SportAPI event object."""
        status_obj = event.get("status") or {}
        # SportAPI uses a 'type' field with a 'code' string
        code = status_obj.get("type", "").lower().replace(" ", "")
        return STATUS_MAP.get(code, "ns")

    def _get_score(self, event, side):
        """
        SportAPI stores scores in homeScore / awayScore objects.
        The 'current' key has the running score.
        """
        key  = "{}Score".format(side)
        obj  = event.get(key) or {}
        return obj.get("current") if obj else None

    def _get_minute(self, event):
        """Extract current match minute."""
        time_obj = event.get("time") or {}
        return time_obj.get("current") or time_obj.get("played")

    def _map_event(self, event):
        """Map a SportAPI event object to our normalised MatchScore."""
        home_team = event.get("homeTeam") or {}
        away_team = event.get("awayTeam") or {}
        tournament = event.get("tournament") or {}
        unique_tournament = tournament.get("uniqueTournament") or {}
        season    = event.get("season") or {}
        round_info = event.get("roundInfo") or {}
        venue     = event.get("venue") or {}

        status = self._parse_status(event)

        # Kickoff — SportAPI uses Unix timestamp in 'startTimestamp'
        kickoff_utc = ""
        ts = event.get("startTimestamp")
        if ts:
            try:
                kickoff_utc = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
            except Exception:
                kickoff_utc = str(ts)

        return MatchScore(
            match_id         = str(event.get("id", "")),
            home_team        = home_team.get("name", "Unknown"),
            away_team        = away_team.get("name", "Unknown"),
            home_team_id     = str(home_team.get("id", "")),
            away_team_id     = str(away_team.get("id", "")),
            home_score       = self._get_score(event, "home"),
            away_score       = self._get_score(event, "away"),
            status           = status,
            minute           = self._get_minute(event),
            competition      = unique_tournament.get("name") or tournament.get("name", ""),
            competition_id   = str(unique_tournament.get("id") or tournament.get("id", "")),
            kickoff_utc      = kickoff_utc,
            venue            = venue.get("city", {}).get("name") if isinstance(venue.get("city"), dict) else None,
            round            = str(round_info.get("round", "")) if round_info else None,
            home_logo        = self._team_logo_url(home_team.get("id")),
            away_logo        = self._team_logo_url(away_team.get("id")),
            competition_logo = self._tournament_logo_url(unique_tournament.get("id")),
            extra={
                "slug":       event.get("slug", ""),
                "season_id":  season.get("id"),
                "tournament": tournament.get("name", ""),
            },
        )

    def _team_logo_url(self, team_id):
        if not team_id:
            return None
        return "https://api.sofascore.app/api/v1/team/{}/image".format(team_id)

    def _tournament_logo_url(self, tournament_id):
        if not tournament_id:
            return None
        return "https://api.sofascore.app/api/v1/unique-tournament/{}/image".format(tournament_id)

    # ── Live scores ───────────────────────────────────────────

    def get_live_scores(self, sport="football"):
        """GET /api/v1/sport/football/events/live"""
        try:
            data   = self._get("api/v1/sport/football/events/live")
            events = data.get("events") or []
            logger.info("SportAPI: {} live events".format(len(events)))
            return [self._map_event(e) for e in events]
        except Exception as e:
            logger.error("get_live_scores failed: {}".format(e))
            return []

    # ── Fixtures ──────────────────────────────────────────────

    def get_fixtures(self, date_from, date_to, sport="football"):
        """
        GET /api/v1/sport/football/scheduled-events/{date}
        Fetches today + next 3 days and merges results.
        """
        results = []
        seen    = set()

        try:
            start = datetime.strptime(date_from, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            end   = datetime.strptime(date_to,   "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except Exception:
            start = datetime.now(timezone.utc)
            end   = start + timedelta(days=3)

        current = start
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            try:
                data   = self._get("api/v1/sport/football/scheduled-events/{}".format(date_str))
                events = data.get("events") or []
                for e in events:
                    eid = e.get("id")
                    if eid and eid not in seen:
                        seen.add(eid)
                        results.append(self._map_event(e).to_dict())
            except Exception as ex:
                logger.warning("Fixtures failed for {}: {}".format(date_str, ex))
            current += timedelta(days=1)

        results.sort(key=lambda x: x.get("kickoff_utc") or "")
        logger.info("SportAPI: {} fixtures ({} to {})".format(len(results), date_from, date_to))
        return results

    # ── Match detail ──────────────────────────────────────────

    def get_fixture_detail(self, fixture_id):
        """
        Fetch full match detail: score + events + statistics.
        Uses separate endpoints for incidents and stats.
        """
        try:
            # Base event
            data  = self._get("api/v1/event/{}".format(fixture_id))
            event = data.get("event")
            if not event:
                return {}
            score_obj = self._map_event(event)

            # Incidents (goals, cards, substitutions)
            events = []
            try:
                inc_data  = self._get("api/v1/event/{}/incidents".format(fixture_id))
                incidents = inc_data.get("incidents") or []
                for inc in incidents:
                    inc_type = inc.get("incidentType", "").lower()
                    events.append({
                        "time":   inc.get("time"),
                        "team":   "home" if inc.get("isHome") else "away",
                        "player": (inc.get("player") or {}).get("name"),
                        "assist": (inc.get("assist1") or {}).get("name"),
                        "type":   inc_type,
                        "detail": inc.get("incidentClass", ""),
                    })
            except Exception as ex:
                logger.warning("Incidents fetch failed: {}".format(ex))

            # Statistics
            stats = {}
            try:
                stat_data   = self._get("api/v1/event/{}/statistics".format(fixture_id))
                stat_groups = stat_data.get("statistics") or []
                for period in stat_groups:
                    if period.get("period", "") != "ALL":
                        continue
                    for group in (period.get("groups") or []):
                        for item in (group.get("statisticsItems") or []):
                            name = item.get("name", "")
                            home_val = item.get("home")
                            away_val = item.get("away")
                            home_name = (event.get("homeTeam") or {}).get("name", "home")
                            away_name = (event.get("awayTeam") or {}).get("name", "away")
                            stats.setdefault(home_name, {})[name] = home_val
                            stats.setdefault(away_name, {})[name] = away_val
            except Exception as ex:
                logger.warning("Statistics fetch failed: {}".format(ex))

            return {**score_obj.to_dict(), "events": events, "statistics": stats}

        except Exception as e:
            logger.error("get_fixture_detail failed ({}): {}".format(fixture_id, e))
            return {}

    # ── Lineups ───────────────────────────────────────────────

    def get_lineups(self, fixture_id):
        """GET /api/v1/event/{id}/lineups"""
        try:
            data    = self._get("api/v1/event/{}/lineups".format(fixture_id))
            lineups = {}

            for side in ("home", "away"):
                team_data = data.get(side) or {}
                team_name = (team_data.get("team") or {}).get("name", side)
                players   = team_data.get("players") or []

                start_xi    = []
                substitutes = []
                for p in players:
                    player_obj = p.get("player") or {}
                    stats_obj  = p.get("statistics") or {}
                    entry = {
                        "number": p.get("shirtNumber"),
                        "name":   player_obj.get("name"),
                        "pos":    p.get("position"),
                        "grid":   p.get("positionString"),
                    }
                    if p.get("substitute", False):
                        substitutes.append(entry)
                    else:
                        start_xi.append(entry)

                lineups[team_name] = {
                    "formation":   team_data.get("formation"),
                    "coach":       (team_data.get("supportStaff") or [{}])[0].get("name") if team_data.get("supportStaff") else None,
                    "start_xi":    start_xi,
                    "substitutes": substitutes,
                }

            return lineups
        except Exception as e:
            logger.error("get_lineups failed ({}): {}".format(fixture_id, e))
            return {}

    # ── Standings ─────────────────────────────────────────────

    def get_standings(self, competition_id, season):
        """
        GET /api/v1/unique-tournament/{id}/season/{season_id}/standings/total
        Resolve season_id from FEATURED_TOURNAMENTS list.
        """
        try:
            # Look up season_id from our featured list
            season_id = None
            for t in FEATURED_TOURNAMENTS:
                if str(t["id"]) == str(competition_id):
                    season_id = t["season_id"]
                    break
            if not season_id:
                season_id = season   # try using it directly

            data  = self._get(
                "api/v1/unique-tournament/{}/season/{}/standings/total".format(
                    competition_id, season_id
                )
            )
            standings_raw = data.get("standings") or []
            if not standings_raw:
                return {}

            groups = []
            for standing in standings_raw:
                rows = standing.get("rows") or []
                group = []
                for row in rows:
                    team = row.get("team") or {}
                    group.append({
                        "rank":            row.get("position"),
                        "team_id":         str(team.get("id", "")),
                        "team_name":       team.get("name", ""),
                        "team_logo":       self._team_logo_url(team.get("id")),
                        "played":          row.get("matches", 0),
                        "won":             row.get("wins", 0),
                        "drawn":           row.get("draws", 0),
                        "lost":            row.get("losses", 0),
                        "goals_for":       row.get("scoresFor", 0),
                        "goals_against":   row.get("scoresAgainst", 0),
                        "goal_difference": row.get("scoreDiffFormatted", 0),
                        "points":          row.get("points", 0),
                        "form":            "".join([
                            r.get("result", "") for r in (row.get("promotion") or [])
                        ]) if row.get("promotion") else "",
                        "description":     (row.get("promotion") or {}).get("text", "") if isinstance(row.get("promotion"), dict) else "",
                    })
                groups.append(group)

            return {"groups": groups}

        except Exception as e:
            logger.error("get_standings failed: {}".format(e))
            return {}

    # ── Team ──────────────────────────────────────────────────

    def get_team(self, team_id):
        """GET /api/v1/team/{id}"""
        try:
            data = self._get("api/v1/team/{}".format(team_id))
            team = data.get("team") or {}
            if not team:
                return {}

            venue   = team.get("venue") or {}
            country = team.get("country") or {}
            city    = venue.get("city") or {}

            return {
                "id":      str(team.get("id", "")),
                "name":    team.get("name", ""),
                "code":    team.get("nameCode", ""),
                "country": country.get("name", ""),
                "founded": team.get("foundationDateTimestamp"),
                "logo":    self._team_logo_url(team.get("id")),
                "venue": {
                    "name":     venue.get("name", ""),
                    "city":     city.get("name", "") if isinstance(city, dict) else "",
                    "capacity": venue.get("capacity"),
                    "image":    None,
                },
            }
        except Exception as e:
            logger.error("get_team failed ({}): {}".format(team_id, e))
            return {}

    # ── Team fixtures ─────────────────────────────────────────

    def get_team_fixtures(self, team_id, last=5, next=5):
        """
        GET /api/v1/team/{id}/events/last/0  — recent results
        GET /api/v1/team/{id}/events/next/0  — upcoming fixtures
        """
        result = {"last": [], "next": []}
        try:
            last_data = self._get("api/v1/team/{}/events/last/0".format(team_id))
            for e in (last_data.get("events") or [])[-last:]:
                result["last"].append(self._map_event(e).to_dict())
        except Exception as e:
            logger.warning("Team last events failed: {}".format(e))

        try:
            next_data = self._get("api/v1/team/{}/events/next/0".format(team_id))
            for e in (next_data.get("events") or [])[:next]:
                result["next"].append(self._map_event(e).to_dict())
        except Exception as e:
            logger.warning("Team next events failed: {}".format(e))

        return result