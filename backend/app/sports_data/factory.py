"""
Sports Data Provider Factory.

Set FOOTBALL_PROVIDER in .env:
  FOOTBALL_PROVIDER=espn         (default — free, no key needed, 17 sports)
  FOOTBALL_PROVIDER=sportapi     (RapidAPI SportAPI subscription)
  FOOTBALL_PROVIDER=sportmonks   (SportMonks direct)
  FOOTBALL_PROVIDER=apifootball  (API-Football via RapidAPI)
"""
import os
import logging
import importlib
from typing import Dict

logger = logging.getLogger(__name__)

PROVIDER_REGISTRY: Dict = {
    ("football", "espn"):        "app.sports_data.espn.ESPNProvider",
    ("football", "sportapi"):    "app.sports_data.sportapi.SportApiProvider",
    ("football", "sportmonks"):  "app.sports_data.sportmonks.SportMonksProvider",
    ("football", "apifootball"): "app.sports_data.apifootball.ApiFootballProvider",
    # Adding a new sport is one line:
    # ("basketball", "espn"):    "app.sports_data.espn.ESPNProvider",
}

SPORT_PROVIDER_ENV = {
    "football":   "FOOTBALL_PROVIDER",
    "basketball": "BASKETBALL_PROVIDER",
    "tennis":     "TENNIS_PROVIDER",
    "cricket":    "CRICKET_PROVIDER",
}


def _load_class(dotted_path):
    module_path, class_name = dotted_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def get_provider(sport="football"):
    env_var       = SPORT_PROVIDER_ENV.get(sport, "{}_PROVIDER".format(sport.upper()))
    provider_name = os.environ.get(env_var, "espn").lower()
    key           = (sport, provider_name)

    if key not in PROVIDER_REGISTRY:
        logger.warning("No provider for ({}, {}). Falling back to espn.".format(sport, provider_name))
        key = (sport, "espn")

    cls = _load_class(PROVIDER_REGISTRY[key])
    return cls()