-- LiveScore Platform — Database Initialisation
-- Runs automatically on first `docker-compose up`

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ── Sports ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sports (
    id          SERIAL PRIMARY KEY,
    slug        TEXT NOT NULL UNIQUE,
    name        TEXT NOT NULL,
    icon_url    TEXT,
    is_active   BOOLEAN DEFAULT true
);

-- ── Competitions ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS competitions (
    id          SERIAL PRIMARY KEY,
    external_id TEXT NOT NULL,
    sport_id    INT REFERENCES sports(id),
    slug        TEXT NOT NULL UNIQUE,
    name        TEXT NOT NULL,
    country     TEXT,
    season      TEXT,
    logo_url    TEXT,
    is_featured BOOLEAN DEFAULT false,
    meta        JSONB DEFAULT '{}'
);

-- ── Teams ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS teams (
    id          SERIAL PRIMARY KEY,
    external_id TEXT NOT NULL,
    sport_id    INT REFERENCES sports(id),
    slug        TEXT NOT NULL UNIQUE,
    name        TEXT NOT NULL,
    short_name  TEXT,
    country     TEXT,
    logo_url    TEXT,
    meta        JSONB DEFAULT '{}'
);

-- ── Fixtures ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fixtures (
    id              SERIAL PRIMARY KEY,
    external_id     TEXT NOT NULL UNIQUE,
    competition_id  INT REFERENCES competitions(id),
    home_team_id    INT REFERENCES teams(id),
    away_team_id    INT REFERENCES teams(id),
    kickoff_utc     TIMESTAMPTZ NOT NULL,
    venue           TEXT,
    round           TEXT,
    status          TEXT DEFAULT 'ns',
    home_score      SMALLINT,
    away_score      SMALLINT,
    ht_home         SMALLINT,
    ht_away         SMALLINT,
    minute          SMALLINT,
    meta            JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_fixtures_kickoff ON fixtures (kickoff_utc);
CREATE INDEX IF NOT EXISTS idx_fixtures_status  ON fixtures (status) WHERE status = 'live';
CREATE INDEX IF NOT EXISTS idx_fixtures_comp    ON fixtures (competition_id, kickoff_utc);

-- ── Match Events (TimescaleDB hypertable) ───────────────
CREATE TABLE IF NOT EXISTS match_events (
    time        TIMESTAMPTZ NOT NULL,
    fixture_id  INT NOT NULL,
    event_type  TEXT,
    team_id     INT,
    player_name TEXT,
    minute      SMALLINT,
    detail      JSONB DEFAULT '{}'
);

SELECT create_hypertable('match_events', 'time', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_me_fixture ON match_events (fixture_id, time DESC);

-- ── User Subscriptions ──────────────────────────────────
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id          SERIAL PRIMARY KEY,
    user_id     TEXT NOT NULL UNIQUE,
    tier        TEXT DEFAULT 'free',
    started_at  TIMESTAMPTZ DEFAULT now(),
    expires_at  TIMESTAMPTZ,
    stripe_subscription_id TEXT
);

-- ── Seed Data — Sports ──────────────────────────────────
INSERT INTO sports (slug, name, is_active) VALUES
    ('football',   'Football',   true),
    ('basketball', 'Basketball', false),
    ('tennis',     'Tennis',     false),
    ('cricket',    'Cricket',    false)
ON CONFLICT (slug) DO NOTHING;
