"""Data access module for the OpenWeather API mock service.

Returns OpenWeather-style JSON shapes (`weather`, `main`, `wind`, `name`, etc.).
"""

import csv
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_str, strict_float, strict_int)

_store = get_store("openweather-api")
_API = "openweather-api"

_store.register("cities", primary_key="id",
                initial_loader=lambda: _coerce_cities(_load("cities.json", "cities")))
_store.register("current", primary_key="city_id",
                initial_loader=lambda: _coerce_current(_load("current_weather.json", "current")))
_store.register("forecast", primary_key="_pk",
                initial_loader=lambda: _coerce_forecast(_load("forecast.json", "forecast")))


def _cities_rows():
    return _store.table("cities").rows()


def _current_rows():
    return _store.table("current").rows()


def _forecast_rows():
    return _store.table("forecast").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_cities(rows):
    out = []
    for r in rows:
        out.append({
            "id": strict_int(r, "id"),
            "name": r["name"],
            "country": r["country"],
            "state": opt_str(r, "state", default="") or None,
            "lat": strict_float(r, "lat"),
            "lon": strict_float(r, "lon"),
            "timezone": strict_int(r, "timezone"),
        })
    return out


def _coerce_current(rows):
    out = []
    for r in rows:
        out.append({
            "city_id": strict_int(r, "city_id"),
            "weather_id": strict_int(r, "weather_id"),
            "weather_main": r["weather_main"],
            "weather_description": r["weather_description"],
            "weather_icon": r["weather_icon"],
            "temp": strict_float(r, "temp"),
            "feels_like": strict_float(r, "feels_like"),
            "temp_min": strict_float(r, "temp_min"),
            "temp_max": strict_float(r, "temp_max"),
            "pressure": strict_int(r, "pressure"),
            "humidity": strict_int(r, "humidity"),
            "wind_speed": strict_float(r, "wind_speed"),
            "wind_deg": strict_int(r, "wind_deg"),
            "clouds": strict_int(r, "clouds"),
            "visibility": strict_int(r, "visibility"),
            "dt": strict_int(r, "dt"),
        })
    return out


def _coerce_forecast(rows):
    out = []
    for r in rows:
        city_id = strict_int(r, "city_id")
        dt = strict_int(r, "dt")
        out.append({
            "_pk": f"{city_id}@{dt}",
            "city_id": city_id,
            "dt": dt,
            "dt_txt": r["dt_txt"],
            "temp": strict_float(r, "temp"),
            "feels_like": strict_float(r, "feels_like"),
            "temp_min": strict_float(r, "temp_min"),
            "temp_max": strict_float(r, "temp_max"),
            "pressure": strict_int(r, "pressure"),
            "humidity": strict_int(r, "humidity"),
            "weather_id": strict_int(r, "weather_id"),
            "weather_main": r["weather_main"],
            "weather_description": r["weather_description"],
            "weather_icon": r["weather_icon"],
            "wind_speed": strict_float(r, "wind_speed"),
            "wind_deg": strict_int(r, "wind_deg"),
            "clouds": strict_int(r, "clouds"),
            "pop": strict_float(r, "pop"),
        })
    return out








# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_city_by_name(q):
    if not q:
        return None
    # q may be "City" or "City,CC"
    name = q.split(",")[0].strip().lower()
    for c in _cities_rows():
        if c["name"].lower() == name:
            return c
    for c in _cities_rows():
        if name in c["name"].lower():
            return c
    return None


def _find_city_by_coords(lat, lon):
    best = None
    best_d = None
    for c in _cities_rows():
        d = (c["lat"] - lat) ** 2 + (c["lon"] - lon) ** 2
        if best_d is None or d < best_d:
            best_d = d
            best = c
    return best


def _current_for(city_id):
    for w in _current_rows():
        if w["city_id"] == city_id:
            return w
    return None


def _weather_block(rec):
    return [{
        "id": rec["weather_id"],
        "main": rec["weather_main"],
        "description": rec["weather_description"],
        "icon": rec["weather_icon"],
    }]


def _current_payload(city, w):
    return {
        "coord": {"lon": city["lon"], "lat": city["lat"]},
        "weather": _weather_block(w),
        "base": "stations",
        "main": {
            "temp": w["temp"],
            "feels_like": w["feels_like"],
            "temp_min": w["temp_min"],
            "temp_max": w["temp_max"],
            "pressure": w["pressure"],
            "humidity": w["humidity"],
        },
        "visibility": w["visibility"],
        "wind": {"speed": w["wind_speed"], "deg": w["wind_deg"]},
        "clouds": {"all": w["clouds"]},
        "dt": w["dt"],
        "sys": {"country": city["country"]},
        "timezone": city["timezone"],
        "id": city["id"],
        "name": city["name"],
        "cod": 200,
    }


def _forecast_item(rec):
    return {
        "dt": rec["dt"],
        "main": {
            "temp": rec["temp"],
            "feels_like": rec["feels_like"],
            "temp_min": rec["temp_min"],
            "temp_max": rec["temp_max"],
            "pressure": rec["pressure"],
            "humidity": rec["humidity"],
        },
        "weather": _weather_block(rec),
        "clouds": {"all": rec["clouds"]},
        "wind": {"speed": rec["wind_speed"], "deg": rec["wind_deg"]},
        "pop": rec["pop"],
        "dt_txt": rec["dt_txt"],
    }


# ---------------------------------------------------------------------------
# Current weather
# ---------------------------------------------------------------------------

def get_current_weather(q=None, lat=None, lon=None):
    if q:
        city = _find_city_by_name(q)
    elif lat is not None and lon is not None:
        city = _find_city_by_coords(lat, lon)
    else:
        return {"cod": "400", "message": "Nothing to geocode"}
    if not city:
        return {"cod": "404", "message": "city not found"}
    w = _current_for(city["id"])
    if not w:
        return {"cod": "404", "message": "city not found"}
    return _current_payload(city, w)


# ---------------------------------------------------------------------------
# Forecast
# ---------------------------------------------------------------------------

def get_forecast(q=None, lat=None, lon=None):
    if q:
        city = _find_city_by_name(q)
    elif lat is not None and lon is not None:
        city = _find_city_by_coords(lat, lon)
    else:
        return {"cod": "400", "message": "Nothing to geocode"}
    if not city:
        return {"cod": "404", "message": "city not found"}
    rows = [r for r in _forecast_rows() if r["city_id"] == city["id"]]
    rows.sort(key=lambda r: r["dt"])
    items = [_forecast_item(r) for r in rows]
    return {
        "cod": "200",
        "message": 0,
        "cnt": len(items),
        "list": items,
        "city": {
            "id": city["id"],
            "name": city["name"],
            "coord": {"lat": city["lat"], "lon": city["lon"]},
            "country": city["country"],
            "timezone": city["timezone"],
        },
    }


# ---------------------------------------------------------------------------
# Geocoding (direct)
# ---------------------------------------------------------------------------

def geocode_direct(q, limit=5):
    name = (q or "").split(",")[0].strip().lower()
    matches = [c for c in _cities_rows() if name and name in c["name"].lower()]
    out = []
    for c in matches[:limit]:
        out.append({
            "name": c["name"],
            "lat": c["lat"],
            "lon": c["lon"],
            "country": c["country"],
            "state": c["state"],
        })
    return out

_store.eager_load()
