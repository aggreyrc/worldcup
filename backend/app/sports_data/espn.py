"""
ESPN Public API Provider
========================
Base: https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/{resource}

NO API KEY REQUIRED — completely free and public.
Covers 17 sports, 139 leagues globally.

Key endpoints used:
  scoreboard              — live + scheduled scores
  scoreboard?dates=YYYYMMDD — fixtures by date
  summary?event={id}      — full match detail, lineups, stats
  standings               — league table (via /apis/v2/)
  teams/{id}              — team profile
  teams/{id}/schedule     — team fixtures

Soccer league slugs (ESPN uses these):
  eng.1  = Premier League
  esp.1  = La Liga
  ger.1  = Bundesliga
  ita.1  = Serie A
  fra.1  = Ligue 1
  uefa.champions_league
  fifa.world
  usa.1  = MLS
  afcon   = Africa Cup of Nations

Compatible with Python 3.8+
"""
import os
import logging
import requests
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from .base import SportsDataProvider, MatchScore

logger = logging.getLogger(__name__)

SITE_API   = "https://site.api.espn.com/apis/site/v2/sports"
SITE_API_V2 = "https://site.api.espn.com/apis/v2/sports"

# ESPN status → our normalised status
STATUS_MAP = {
    "STATUS_SCHEDULED":       "ns",
    "STATUS_IN_PROGRESS":     "live",
    "STATUS_HALFTIME":        "ht",
    "STATUS_END_PERIOD":      "live",
    "STATUS_FINAL":           "ft",
    "STATUS_FULL_TIME":       "ft",
    "STATUS_POSTPONED":       "postponed",
    "STATUS_CANCELED":        "cancelled",
    "STATUS_SUSPENDED":       "postponed",
    "STATUS_DELAYED":         "postponed",
    "STATUS_RAIN_DELAY":      "postponed",
    "STATUS_EXTRA_TIME":      "live",
    "STATUS_PENALTY":         "live",
    "STATUS_ABANDONED":       "cancelled",
    "STATUS_FORFEIT":         "ft",
    "STATUS_END_OF_EXTRATIME":"live",
}

# Featured soccer leagues — (league_slug, display_name)
FEATURED_LEAGUES = [
    ("eng.1",               "Premier League"),
    ("esp.1",               "La Liga"),
    ("ger.1",               "Bundesliga"),
    ("ita.1",               "Serie A"),
    ("fra.1",               "Ligue 1"),
    ("uefa.champions_league","Champions League"),
    ("fifa.world",          "World Cup"),
    ("usa.1",               "MLS"),
    ("ned.1",               "Eredivisie"),
    ("por.1",               "Primeira Liga"),
]


class ESPNProvider(SportsDataProvider):

    def __init__(self):
        # No API key needed — ESPN is fully public
        logger.info("ESPN provider ready (no API key required)")

    def _get(self, url, params=None):
        """GET request to ESPN API — no auth headers needed."""
        try:
            resp = requests.get(
                url,
                params=params or {},
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0 (compatible; LivescoreApp/1.0)"},
            )
            resp.raise_for_status()
            return resp.json()
        except requests.Timeout:
            logger.error("Timeout on {}".format(url))
            raise
        except requests.HTTPError as e:
            logger.error("HTTP {} on {}: {}".format(
                e.response.status_code, url, e.response.text[:200]))
            raise
        except requests.RequestException as e:
            logger.error("Request error on {}: {}".format(url, e))
            raise

    def _parse_status(self, competition):
        """Extract our normalised status from an ESPN competition object."""
        status = competition.get("status") or {}
        stype  = status.get("type") or {}
        state  = stype.get("state", "").lower()       # pre / in / post
        name   = stype.get("name", "")                # STATUS_IN_PROGRESS etc.

        mapped = STATUS_MAP.get(name)
        if mapped:
            return mapped
        if state == "in":
            # Check halftime
            period = status.get("period", 0)
            detail = stype.get("shortDetail", "").lower()
            if "half" in detail or "ht" in detail:
                return "ht"
            return "live"
        if state == "post":
            return "ft"
        return "ns"

    def _get_minute(self, competition):
        """Extract current match minute from ESPN clock."""
        status    = competition.get("status") or {}
        clock_str = status.get("displayClock", "")     # e.g. "67:23"
        if clock_str:
            try:
                return int(clock_str.split(":")[0])
            except (ValueError, IndexError):
                pass
        return None

    def _get_competitor(self, competitors, home_away):
        """Find home or away competitor object."""
        for c in (competitors or []):
            if c.get("homeAway", "").lower() == home_away:
                return c
        return {}

    def _competitor_logo(self, competitor):
        """Extract best logo URL from a competitor."""
        team = competitor.get("team") or {}
        logos = team.get("logos") or []
        if logos:
            return logos[0].get("href")
        return team.get("logo")

    def _map_competition(self, event, competition):
        """Map ESPN event + competition to our MatchScore."""
        competitors = competition.get("competitors") or []
        home_c      = self._get_competitor(competitors, "home")
        away_c      = self._get_competitor(competitors, "away")

        home_team   = home_c.get("team") or {}
        away_team   = away_c.get("team") or {}

        status      = self._parse_status(competition)
        minute      = self._get_minute(competition) if status == "live" else None

        # Scores
        home_score  = None
        away_score  = None
        if home_c.get("score") not in (None, ""):
            try:
                home_score = int(home_c["score"])
            except (ValueError, TypeError):
                pass
        if away_c.get("score") not in (None, ""):
            try:
                away_score = int(away_c["score"])
            except (ValueError, TypeError):
                pass

        # League info from event
        league      = event.get("league") or {}
        league_name = league.get("name", "")
        league_id   = league.get("slug", str(league.get("id", "")))
        league_logo = (league.get("logos") or [{}])[0].get("href") if league.get("logos") else None

        # Kickoff
        kickoff_utc = event.get("date", "")

        # Venue
        venue_obj   = competition.get("venue") or {}
        venue_name  = venue_obj.get("fullName") or venue_obj.get("address", {}).get("city", "")

        return MatchScore(
            match_id         = str(event.get("id", "")),
            home_team        = home_team.get("displayName") or home_team.get("name", "Unknown"),
            away_team        = away_team.get("displayName") or away_team.get("name", "Unknown"),
            home_team_id     = str(home_team.get("id", "")),
            away_team_id     = str(away_team.get("id", "")),
            home_score       = home_score,
            away_score       = away_score,
            status           = status,
            minute           = minute,
            competition      = league_name,
            competition_id   = league_id,
            kickoff_utc      = kickoff_utc,
            venue            = venue_name or None,
            round            = event.get("season", {}).get("slug"),
            home_logo        = self._competitor_logo(home_c),
            away_logo        = self._competitor_logo(away_c),
            competition_logo = league_logo,
            extra={
                "short_name": event.get("shortName", ""),
                "season":     event.get("season", {}).get("year"),
                "league_slug": league_id,
            },
        )

    def _events_from_scoreboard(self, data):
        """Extract all MatchScore objects from a scoreboard response."""
        results = []
        for event in (data.get("events") or []):
            for comp in (event.get("competitions") or []):
                try:
                    results.append(self._map_competition(event, comp))
                except Exception as e:
                    logger.warning("Failed to map event {}: {}".format(
                        event.get("id"), e))
        return results

    # ── Live scores ───────────────────────────────────────────

    def get_live_scores(self, sport="football"):
        """
        Fetch live scores across all featured soccer leagues.
        ESPN scoreboard returns both live and scheduled — we filter for live.
        """
        all_live = []
        seen     = set()

        for league_slug, league_name in FEATURED_LEAGUES:
            try:
                url  = "{}/soccer/{}/scoreboard".format(SITE_API, league_slug)
                data = self._get(url)
                for match in self._events_from_scoreboard(data):
                    if match.match_id not in seen and match.status in ("live", "ht"):
                        seen.add(match.match_id)
                        all_live.append(match)
            except Exception as e:
                logger.warning("Live scores failed for {}: {}".format(league_slug, e))

        logger.info("ESPN: {} live matches".format(len(all_live)))
        return all_live

    # ── Fixtures ──────────────────────────────────────────────

    def get_fixtures(self, date_from, date_to, sport="football"):
        """
        Fetch fixtures between two dates across all featured leagues.
        ESPN scoreboard accepts ?dates=YYYYMMDD for specific dates.
        """
        results = []
        seen    = set()

        # Build list of dates to fetch
        try:
            start = datetime.strptime(date_from, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            end   = datetime.strptime(date_to,   "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except Exception:
            start = datetime.now(timezone.utc)
            end   = start + timedelta(days=3)

        dates = []
        current = start
        while current <= end:
            dates.append(current.strftime("%Y%m%d"))
            current += timedelta(days=1)

        for league_slug, _ in FEATURED_LEAGUES:
            for date_str in dates:
                try:
                    url  = "{}/soccer/{}/scoreboard".format(SITE_API, league_slug)
                    data = self._get(url, {"dates": date_str})
                    for match in self._events_from_scoreboard(data):
                        if match.match_id not in seen:
                            seen.add(match.match_id)
                            results.append(match.to_dict())
                except Exception as e:
                    logger.warning("Fixtures failed for {} {}: {}".format(
                        league_slug, date_str, e))

        results.sort(key=lambda x: x.get("kickoff_utc") or "")
        logger.info("ESPN: {} fixtures ({} to {})".format(len(results), date_from, date_to))
        return results

    # ── Match detail ──────────────────────────────────────────

    def get_fixture_detail(self, fixture_id):
        """
        GET /apis/site/v2/sports/soccer/{league}/summary?event={id}
        Returns full match detail: score, events, stats, lineups.
        We try each league slug until we find the match.
        """
        for league_slug, _ in FEATURED_LEAGUES:
            try:
                url  = "{}/soccer/{}/summary".format(SITE_API, league_slug)
                data = self._get(url, {"event": fixture_id})

                if not data.get("header"):
                    continue

                header       = data.get("header") or {}
                competitions = header.get("competitions") or []
                if not competitions:
                    continue

                comp      = competitions[0]
                event_obj = {"id": fixture_id, "date": header.get("gameDate", ""),
                             "league": header.get("league") or {}}
                score_obj = self._map_competition(event_obj, comp)

                # Play-by-play / events (goals, cards)
                events = []
                for play in (data.get("plays") or []):
                    ptype = play.get("type") or {}
                    events.append({
                        "time":   play.get("clock", {}).get("displayValue"),
                        "team":   (play.get("team") or {}).get("displayName"),
                        "player": (play.get("participants") or [{}])[0].get("athlete", {}).get("displayName"),
                        "assist": None,
                        "type":   ptype.get("text", ""),
                        "detail": play.get("text", ""),
                    })

                # Statistics
                stats = {}
                for team_stats in (data.get("statistics") or []):
                    team_name = (team_stats.get("team") or {}).get("displayName", "")
                    stats[team_name] = {}
                    for stat in (team_stats.get("stats") or []):
                        stats[team_name][stat.get("label", "")] = stat.get("displayValue")

                return {**score_obj.to_dict(), "events": events, "statistics": stats}

            except Exception as e:
                logger.warning("Summary failed for {} on {}: {}".format(
                    fixture_id, league_slug, e))
                continue

        logger.error("Could not find fixture {} in any league".format(fixture_id))
        return {}

    # ── Lineups ───────────────────────────────────────────────

    def get_lineups(self, fixture_id):
        """
        Extract lineups from the ESPN game summary rosters section.
        """
        for league_slug, _ in FEATURED_LEAGUES:
            try:
                url  = "{}/soccer/{}/summary".format(SITE_API, league_slug)
                data = self._get(url, {"event": fixture_id})

                rosters = data.get("rosters") or []
                if not rosters:
                    continue

                lineups = {}
                for team_roster in rosters:
                    team_name = (team_roster.get("team") or {}).get("displayName", "")
                    athletes  = team_roster.get("roster") or []

                    start_xi    = []
                    substitutes = []
                    for a in athletes:
                        athlete = a.get("athlete") or {}
                        pos_obj = a.get("position") or {}
                        entry   = {
                            "number": athlete.get("jersey"),
                            "name":   athlete.get("displayName"),
                            "pos":    pos_obj.get("abbreviation") or pos_obj.get("name"),
                            "grid":   None,
                        }
                        if a.get("starter", False):
                            start_xi.append(entry)
                        else:
                            substitutes.append(entry)

                    lineups[team_name] = {
                        "formation":   team_roster.get("formation"),
                        "coach":       (team_roster.get("coach") or [{}])[0].get("name") if team_roster.get("coach") else None,
                        "start_xi":    start_xi,
                        "substitutes": substitutes,
                    }

                if lineups:
                    return lineups

            except Exception as e:
                logger.warning("Lineups failed for {} on {}: {}".format(
                    fixture_id, league_slug, e))
                continue

        return {}

    # ── Standings ─────────────────────────────────────────────

    def get_standings(self, competition_id, season):
        """
        GET https://site.api.espn.com/apis/v2/sports/soccer/{league}/standings
        competition_id can be a league slug (eng.1) or numeric ESPN league ID.
        """
        # Map numeric IDs back to slugs if needed
        id_to_slug = {
            "39": "eng.1", "140": "esp.1", "78": "ger.1",
            "135": "ita.1", "61": "fra.1", "2": "uefa.champions_league",
            "1": "fifa.world", "17": "eng.1", "564": "esp.1",
        }
        league_slug = id_to_slug.get(str(competition_id), str(competition_id))

        try:
            url  = "{}/soccer/{}/standings".format(SITE_API_V2, league_slug)
            data = self._get(url, {"season": season})

            children = data.get("children") or []
            # Some leagues return nested groups (e.g. World Cup)
            if not children:
                children = [data]

            groups = []
            for child in children:
                standings_raw = child.get("standings") or {}
                entries       = standings_raw.get("entries") or []
                if not entries:
                    continue

                group = []
                for entry in entries:
                    team    = entry.get("team") or {}
                    stats   = {s["name"]: s.get("value", 0)
                               for s in (entry.get("stats") or [])}
                    logos   = team.get("logos") or []
                    logo_url = logos[0].get("href") if logos else None

                    group.append({
                        "rank":            int(stats.get("rank", 0)),
                        "team_id":         str(team.get("id", "")),
                        "team_name":       team.get("displayName") or team.get("name", ""),
                        "team_logo":       logo_url,
                        "played":          int(stats.get("gamesPlayed", 0)),
                        "won":             int(stats.get("wins", 0)),
                        "drawn":           int(stats.get("ties", 0)),
                        "lost":            int(stats.get("losses", 0)),
                        "goals_for":       int(stats.get("pointsFor", 0)),
                        "goals_against":   int(stats.get("pointsAgainst", 0)),
                        "goal_difference": int(stats.get("pointDifferential", 0)),
                        "points":          int(stats.get("points", 0)),
                        "form":            "",
                        "description":     entry.get("note", {}).get("description", "") if isinstance(entry.get("note"), dict) else "",
                    })

                if group:
                    groups.append(group)

            return {"groups": groups}

        except Exception as e:
            logger.error("get_standings failed ({}): {}".format(competition_id, e))
            return {}

    # ── Team ──────────────────────────────────────────────────

    def get_team(self, team_id):
        """
        GET /apis/site/v2/sports/soccer/{league}/teams/{id}
        Try each league until found.
        """
        for league_slug, _ in FEATURED_LEAGUES:
            try:
                url  = "{}/soccer/{}/teams/{}".format(SITE_API, league_slug, team_id)
                data = self._get(url)
                team = (data.get("team") or data.get("sports", [{}])[0]
                        .get("leagues", [{}])[0].get("teams", [{}])[0].get("team"))
                if not team:
                    continue

                logos    = team.get("logos") or []
                logo_url = logos[0].get("href") if logos else None
                venue    = team.get("venue") or {}
                addr     = venue.get("address") or {}

                return {
                    "id":      str(team.get("id", "")),
                    "name":    team.get("displayName") or team.get("name", ""),
                    "code":    team.get("abbreviation", ""),
                    "country": team.get("location", ""),
                    "founded": None,
                    "logo":    logo_url,
                    "venue": {
                        "name":     venue.get("fullName", ""),
                        "city":     addr.get("city", ""),
                        "capacity": venue.get("capacity"),
                        "image":    None,
                    },
                }
            except Exception:
                continue

        return {}

    def get_team_fixtures(self, team_id, last=5, next=5):
        """GET /apis/site/v2/sports/soccer/{league}/teams/{id}/schedule"""
        result = {"last": [], "next": []}
        for league_slug, _ in FEATURED_LEAGUES:
            try:
                url  = "{}/soccer/{}/teams/{}/schedule".format(SITE_API, league_slug, team_id)
                data = self._get(url)
                events = data.get("events") or []
                if not events:
                    continue

                now = datetime.now(timezone.utc)
                past = []
                upcoming = []

                for event in events:
                    for comp in (event.get("competitions") or []):
                        match = self._map_competition(event, comp)
                        try:
                            kickoff = datetime.fromisoformat(
                                match.kickoff_utc.replace("Z", "+00:00"))
                            if kickoff < now:
                                past.append(match.to_dict())
                            else:
                                upcoming.append(match.to_dict())
                        except Exception:
                            upcoming.append(match.to_dict())

                result["last"] = past[-last:]
                result["next"] = upcoming[:next]
                return result

            except Exception as e:
                logger.warning("Team schedule failed for {} {}: {}".format(
                    team_id, league_slug, e))
                continue

        return result