"""
Sports Data Provider — Abstract Base Class.
Compatible with Python 3.8+.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class MatchScore:
    """Normalised live match score returned by any provider."""
    match_id: str
    home_team: str
    away_team: str
    home_team_id: str
    away_team_id: str
    home_score: Optional[int]
    away_score: Optional[int]
    status: str          # ns | live | ht | ft | postponed | cancelled
    minute: Optional[int]
    competition: str
    competition_id: str
    kickoff_utc: str
    venue: Optional[str] = None
    round: Optional[str] = None
    home_logo: Optional[str] = None
    away_logo: Optional[str] = None
    competition_logo: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "match_id":         self.match_id,
            "home_team":        self.home_team,
            "away_team":        self.away_team,
            "home_team_id":     self.home_team_id,
            "away_team_id":     self.away_team_id,
            "home_score":       self.home_score,
            "away_score":       self.away_score,
            "status":           self.status,
            "minute":           self.minute,
            "competition":      self.competition,
            "competition_id":   self.competition_id,
            "kickoff_utc":      self.kickoff_utc,
            "venue":            self.venue,
            "round":            self.round,
            "home_logo":        self.home_logo,
            "away_logo":        self.away_logo,
            "competition_logo": self.competition_logo,
            "extra":            self.extra,
        }


class SportsDataProvider(ABC):
    """Abstract interface for all sports data providers."""

    @abstractmethod
    def get_live_scores(self, sport: str = "football") -> List[MatchScore]:
        ...

    @abstractmethod
    def get_fixtures(self, date_from: str, date_to: str, sport: str = "football") -> List[Dict]:
        ...

    @abstractmethod
    def get_fixture_detail(self, fixture_id: str) -> Dict:
        ...

    @abstractmethod
    def get_lineups(self, fixture_id: str) -> Dict:
        ...

    @abstractmethod
    def get_standings(self, competition_id: str, season: str) -> Dict:
        ...

    @abstractmethod
    def get_team(self, team_id: str) -> Dict:
        ...

    @abstractmethod
    def get_team_fixtures(self, team_id: str, last: int = 5, next: int = 5) -> Dict:
        ...