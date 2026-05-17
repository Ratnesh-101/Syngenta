# backend/core/integrations/weather.py
"""
Real-world weather integration via Open-Meteo (https://open-meteo.com).

Free, no API key, no rate limits for our scale. Returns a normalized
0.0-1.0 "weather risk score" for a given lat/lon, where higher = more
adverse conditions for crop / field-rep operations over the next 7 days.

Used by db/seed_data.py to replace the previous random.uniform() call.
"""
from __future__ import annotations

import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Bikaner, Rajasthan (the demo territory)
BIKANER_LAT = 28.0229
BIKANER_LON = 73.3119


def fetch_weather_risk_score(
    lat: float = BIKANER_LAT,
    lon: float = BIKANER_LON,
    timeout_seconds: float = 5.0,
) -> Optional[float]:
    """Fetch a 7-day forecast and return a single normalized risk score
    in [0.0, 1.0], or None if the API is unreachable.

    Components (each contributes equally to the final score):
      - Precipitation risk: heavier expected rainfall → higher
      - Heat stress: more days above 38°C → higher
      - Wind risk: higher peak wind gusts → higher

    Caller is expected to handle None by falling back to a default.
    """
    try:
        resp = requests.get(
            OPEN_METEO_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": ",".join([
                    "precipitation_sum",
                    "temperature_2m_max",
                    "wind_speed_10m_max",
                ]),
                "forecast_days": 7,
                "timezone": "Asia/Kolkata",
            },
            timeout=timeout_seconds,
        )
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError) as e:
        logger.warning("Open-Meteo fetch failed: %s", e)
        return None

    daily = data.get("daily") or {}
    precipitation = daily.get("precipitation_sum") or []
    temperature_max = daily.get("temperature_2m_max") or []
    wind_max = daily.get("wind_speed_10m_max") or []

    if not (precipitation and temperature_max and wind_max):
        logger.warning("Open-Meteo returned no usable daily data")
        return None

    # ---- 1. Precipitation risk ----
    # Total 7-day precipitation in mm. 0mm = 0.0, 100mm+ = 1.0
    total_precip = sum(precipitation)
    precip_risk = min(1.0, total_precip / 100.0)

    # ---- 2. Heat stress risk ----
    # Days above 38°C in the next 7 days. 0 days = 0.0, 5+ days = 1.0
    hot_days = sum(1 for t in temperature_max if t is not None and t >= 38.0)
    heat_risk = min(1.0, hot_days / 5.0)

    # ---- 3. Wind risk ----
    # Peak wind speed in km/h. 0 = 0.0, 60+ = 1.0
    peak_wind = max((w for w in wind_max if w is not None), default=0.0)
    wind_risk = min(1.0, peak_wind / 60.0)

    # Final score: equal-weighted average of the three components
    score = (precip_risk + heat_risk + wind_risk) / 3.0
    return round(score, 2)


def fetch_weather_summary(
    lat: float = BIKANER_LAT,
    lon: float = BIKANER_LON,
) -> Optional[dict]:
    """Returns a dict with the score and the underlying numbers, for
    transparency / dashboard display. Used during seeding logs so the
    demo can defend the number on stage.
    """
    try:
        resp = requests.get(
            OPEN_METEO_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": ",".join([
                    "precipitation_sum",
                    "temperature_2m_max",
                    "wind_speed_10m_max",
                ]),
                "forecast_days": 7,
                "timezone": "Asia/Kolkata",
            },
            timeout=5.0,
        )
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return None

    daily = data.get("daily") or {}
    precipitation = daily.get("precipitation_sum") or []
    temperature_max = daily.get("temperature_2m_max") or []
    wind_max = daily.get("wind_speed_10m_max") or []
    if not (precipitation and temperature_max and wind_max):
        return None

    total_precip = sum(precipitation)
    hot_days = sum(1 for t in temperature_max if t is not None and t >= 38.0)
    peak_wind = max((w for w in wind_max if w is not None), default=0.0)

    precip_risk = min(1.0, total_precip / 100.0)
    heat_risk = min(1.0, hot_days / 5.0)
    wind_risk = min(1.0, peak_wind / 60.0)
    score = round((precip_risk + heat_risk + wind_risk) / 3.0, 2)

    return {
        "score": score,
        "components": {
            "total_precipitation_mm_7d": round(total_precip, 1),
            "hot_days_above_38c_7d": hot_days,
            "peak_wind_kmh_7d": round(peak_wind, 1),
        },
        "raw": {
            "precipitation_sum": precipitation,
            "temperature_2m_max": temperature_max,
            "wind_speed_10m_max": wind_max,
        },
        "source": "Open-Meteo",
        "location": {"lat": lat, "lon": lon},
    }