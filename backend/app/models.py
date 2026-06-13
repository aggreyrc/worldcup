"""
Database models — PostgreSQL via SQLAlchemy.
TimescaleDB hypertable for match_events is created in init.sql migration.
"""
from datetime import datetime, timezone
from app import db


class Sport(db.Model):
    __tablename__ = "sports"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.Text, unique=True, nullable=False)   # "football"
    name = db.Column(db.Text, nullable=False)
    icon_url = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)

    competitions = db.relationship("Competition", back_populates="sport", lazy="dynamic")

    def to_dict(self):
        return {"id": self.id, "slug": self.slug, "name": self.name, "icon_url": self.icon_url}


class Competition(db.Model):
    __tablename__ = "competitions"

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.Text, nullable=False)
    sport_id = db.Column(db.Integer, db.ForeignKey("sports.id"), nullable=False)
    slug = db.Column(db.Text, unique=True, nullable=False)   # "premier-league"
    name = db.Column(db.Text, nullable=False)
    country = db.Column(db.Text)
    season = db.Column(db.Text)
    logo_url = db.Column(db.Text)
    is_featured = db.Column(db.Boolean, default=False)
    meta = db.Column(db.JSON, default=dict)

    sport = db.relationship("Sport", back_populates="competitions")
    fixtures = db.relationship("Fixture", back_populates="competition", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "country": self.country,
            "season": self.season,
            "logo_url": self.logo_url,
            "is_featured": self.is_featured,
            "sport": self.sport.slug if self.sport else None,
        }


class Team(db.Model):
    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.Text, nullable=False)
    sport_id = db.Column(db.Integer, db.ForeignKey("sports.id"), nullable=False)
    slug = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    short_name = db.Column(db.Text)
    country = db.Column(db.Text)
    logo_url = db.Column(db.Text)
    meta = db.Column(db.JSON, default=dict)   # colours, stadium, founded

    sport = db.relationship("Sport")

    def to_dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "short_name": self.short_name,
            "country": self.country,
            "logo_url": self.logo_url,
            "meta": self.meta,
        }


class Fixture(db.Model):
    __tablename__ = "fixtures"
    __table_args__ = (
        db.Index("idx_fixtures_kickoff", "kickoff_utc"),
        db.Index("idx_fixtures_status", "status"),
    )

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.Text, unique=True, nullable=False)
    competition_id = db.Column(db.Integer, db.ForeignKey("competitions.id"))
    home_team_id = db.Column(db.Integer, db.ForeignKey("teams.id"))
    away_team_id = db.Column(db.Integer, db.ForeignKey("teams.id"))
    kickoff_utc = db.Column(db.DateTime(timezone=True), nullable=False)
    venue = db.Column(db.Text)
    round = db.Column(db.Text)
    status = db.Column(db.Text, default="ns")   # ns|live|ht|ft|postponed
    home_score = db.Column(db.SmallInteger)
    away_score = db.Column(db.SmallInteger)
    ht_home = db.Column(db.SmallInteger)
    ht_away = db.Column(db.SmallInteger)
    minute = db.Column(db.SmallInteger)
    meta = db.Column(db.JSON, default=dict)    # xG, possession, shots

    competition = db.relationship("Competition", back_populates="fixtures")
    home_team = db.relationship("Team", foreign_keys=[home_team_id])
    away_team = db.relationship("Team", foreign_keys=[away_team_id])

    def to_dict(self):
        return {
            "id": self.external_id,
            "competition": self.competition.to_dict() if self.competition else {},
            "home_team": self.home_team.to_dict() if self.home_team else {},
            "away_team": self.away_team.to_dict() if self.away_team else {},
            "kickoff_utc": self.kickoff_utc.isoformat() if self.kickoff_utc else None,
            "venue": self.venue,
            "round": self.round,
            "status": self.status,
            "home_score": self.home_score,
            "away_score": self.away_score,
            "ht_home": self.ht_home,
            "ht_away": self.ht_away,
            "minute": self.minute,
            "meta": self.meta,
        }


class UserSubscription(db.Model):
    __tablename__ = "user_subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Text, nullable=False, unique=True)
    tier = db.Column(db.Text, default="free")  # free | plus | pro
    started_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime(timezone=True))
    stripe_subscription_id = db.Column(db.Text)
