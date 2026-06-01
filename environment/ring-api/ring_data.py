"""Data access module for Ring API simulation."""

import csv
import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


# ---------------------------------------------------------------------------
# Load and coerce data
# ---------------------------------------------------------------------------

def _coerce_events(rows):
    out = []
    for r in rows:
        out.append({
            "id": int(r["id"]),
            "doorbot_id": int(r["doorbot_id"]),
            "device_id": r["device_id"],
            "kind": r["kind"],
            "created_at": r["created_at"],
            "answered": r["answered"].lower() == "true",
            "favorite": r["favorite"].lower() == "true",
            "recording": {"status": r["recording_status"]},
            "snapshot_url": r["snapshot_url"],
            "duration_seconds": int(r["duration_seconds"]) if r["duration_seconds"] else None,
            "cv_properties": r["cv_properties"] if r["cv_properties"] else None,
        })
    return out


def _coerce_shared_users(rows):
    out = []
    for r in rows:
        out.append({
            "user_id": int(r["user_id"]),
            "first_name": r["first_name"],
            "last_name": r["last_name"],
            "email": r["email"],
            "role": r["role"],
            "device_access": r["device_access"],
            "shared_at": r["shared_at"],
        })
    return out


def _coerce_motion_zones(rows):
    out = []
    for r in rows:
        out.append({
            "device_id": int(r["device_id"]),
            "zone_id": r["zone_id"],
            "zone_name": r["zone_name"],
            "sensitivity": int(r["sensitivity"]),
            "enabled": r["enabled"].lower() == "true",
            "coordinates": r["coordinates"],
        })
    return out


def _coerce_notification_prefs(rows):
    out = []
    for r in rows:
        out.append({
            "device_id": int(r["device_id"]),
            "motion_alerts": r["motion_alerts"].lower() == "true" if r["motion_alerts"] else None,
            "ding_alerts": r["ding_alerts"].lower() == "true" if r["ding_alerts"] else None,
            "person_alerts": r["person_alerts"].lower() == "true" if r["person_alerts"] else None,
            "package_alerts": r["package_alerts"].lower() == "true" if r["package_alerts"] else None,
        })
    return out


# Load all data at module init
with open(DATA_DIR / "devices.json", encoding="utf-8") as _f:
    _devices_raw = json.load(_f)

with open(DATA_DIR / "location.json", encoding="utf-8") as _f:
    _location_raw = json.load(_f)

with open(DATA_DIR / "active_dings.json", encoding="utf-8") as _f:
    _active_dings_raw = json.load(_f)

_events = _coerce_events(_load("events.csv"))
_shared_users = _coerce_shared_users(_load("shared_users.csv"))
_motion_zones = _coerce_motion_zones(_load("motion_zones.csv"))
_notification_prefs = _coerce_notification_prefs(_load("notification_prefs.csv"))

# Mutable in-memory stores
_devices_store = deepcopy(_devices_raw)
_location_store = deepcopy(_location_raw)
_active_dings_store = deepcopy(_active_dings_raw)
_events_store = deepcopy(_events)
_shared_users_store = deepcopy(_shared_users)
_motion_zones_store = deepcopy(_motion_zones)
_notification_prefs_store = deepcopy(_notification_prefs)

_next_event_id = max(e["id"] for e in _events_store) + 1


# ---------------------------------------------------------------------------
# Helper: get all devices as flat list
# ---------------------------------------------------------------------------

def _all_devices():
    devices = []
    for d in _devices_store.get("doorbots", []):
        devices.append({**d, "device_type": "doorbot"})
    for d in _devices_store.get("stickup_cams", []):
        devices.append({**d, "device_type": "stickup_cam"})
    for d in _devices_store.get("chimes", []):
        devices.append({**d, "device_type": "chime"})
    return devices


def _find_device(device_id):
    for category in ["doorbots", "stickup_cams", "chimes"]:
        for d in _devices_store.get(category, []):
            if d["id"] == device_id:
                return d, category
    return None, None


# ---------------------------------------------------------------------------
# Devices
# ---------------------------------------------------------------------------

def list_devices():
    return _devices_store


def get_device(device_id: int):
    device, category = _find_device(device_id)
    if not device:
        return {"error": f"Device {device_id} not found"}
    return {"type": "device", "device_type": category, "device": device}


def get_device_health(device_id: int):
    device, category = _find_device(device_id)
    if not device:
        return {"error": f"Device {device_id} not found"}
    health = {
        "device_id": device_id,
        "firmware_version": device.get("firmware_version"),
        "battery_life": device.get("battery_life"),
        "wifi_signal_strength": device.get("wifi_signal_strength", -45),
        "wifi_signal_category": device.get("wifi_signal_category", "good"),
        "alerts": device.get("alerts", {}),
        "external_connection": device.get("external_connection", False),
    }
    return {"type": "device_health", "device_health": health}


def update_device_settings(device_id: int, data: dict):
    device, category = _find_device(device_id)
    if not device:
        return {"error": f"Device {device_id} not found"}
    updatable = {
        "motion_sensitivity", "motion_detection_enabled", "people_detection_enabled",
        "package_detection_enabled", "led_status", "light_schedule_enabled",
        "light_on_duration_seconds",
    }
    settings = device.get("settings", {})
    for k, v in data.items():
        if k in updatable:
            settings[k] = v
        elif k == "led_status":
            device["led_status"] = v
    device["settings"] = settings
    return {"type": "device", "device_type": category, "device": device}


# ---------------------------------------------------------------------------
# Locations
# ---------------------------------------------------------------------------

def get_location(location_id: str):
    if location_id != _location_store["location_id"]:
        return {"error": f"Location {location_id} not found"}
    return {"type": "location", "location": _location_store}


def list_location_devices(location_id: str):
    if location_id != _location_store["location_id"]:
        return {"error": f"Location {location_id} not found"}
    return _devices_store


def get_location_mode(location_id: str):
    if location_id != _location_store["location_id"]:
        return {"error": f"Location {location_id} not found"}
    return {"type": "mode", "mode": _location_store["mode"], "location_id": location_id}


def set_location_mode(location_id: str, mode: str):
    if location_id != _location_store["location_id"]:
        return {"error": f"Location {location_id} not found"}
    valid_modes = ["home", "away", "disarmed"]
    if mode not in valid_modes:
        return {"error": f"Invalid mode '{mode}'. Must be one of: {valid_modes}"}
    _location_store["mode"] = mode
    _location_store["updated_at"] = _now()
    return {"type": "mode", "mode": _location_store["mode"], "location_id": location_id}


# ---------------------------------------------------------------------------
# Event History
# ---------------------------------------------------------------------------

def list_device_events(
    device_id: int,
    kind: str = None,
    date_from: str = None,
    date_to: str = None,
    limit: int = 20,
    offset: int = 0,
):
    results = [e for e in _events_store if e["doorbot_id"] == device_id]

    if kind:
        results = [e for e in results if e["kind"] == kind]
    if date_from:
        results = [e for e in results if e["created_at"] >= date_from]
    if date_to:
        results = [e for e in results if e["created_at"] <= date_to]

    # Sort newest first
    results = sorted(results, key=lambda x: x["created_at"], reverse=True)

    total = len(results)
    page_results = results[offset: offset + limit]
    return {
        "type": "events",
        "count": len(page_results),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page_results,
    }


def get_event(event_id: int):
    for e in _events_store:
        if e["id"] == event_id:
            return {"type": "event", "event": e}
    return {"error": f"Event {event_id} not found"}


def get_event_recording(event_id: int):
    for e in _events_store:
        if e["id"] == event_id:
            if e["recording"]["status"] != "ready":
                return {"error": f"Recording not available for event {event_id}"}
            location_id = _location_store["location_id"]
            url = f"https://ring-recordings.s3.amazonaws.com/{location_id}/{e['device_id']}/{event_id}.mp4"
            return {"type": "recording", "event_id": event_id, "recording_url": url}
    return {"error": f"Event {event_id} not found"}


# ---------------------------------------------------------------------------
# Active Dings
# ---------------------------------------------------------------------------

def list_active_dings():
    return _active_dings_store


# ---------------------------------------------------------------------------
# Recordings
# ---------------------------------------------------------------------------

def list_recordings(device_id: int, date_from: str = None, date_to: str = None):
    events = [e for e in _events_store if e["doorbot_id"] == device_id and e["recording"]["status"] == "ready"]

    if date_from:
        events = [e for e in events if e["created_at"] >= date_from]
    if date_to:
        events = [e for e in events if e["created_at"] <= date_to]

    events = sorted(events, key=lambda x: x["created_at"], reverse=True)

    location_id = _location_store["location_id"]
    recordings = []
    for e in events:
        recordings.append({
            "event_id": e["id"],
            "doorbot_id": e["doorbot_id"],
            "device_id": e["device_id"],
            "kind": e["kind"],
            "created_at": e["created_at"],
            "duration_seconds": e["duration_seconds"],
            "recording_url": f"https://ring-recordings.s3.amazonaws.com/{location_id}/{e['device_id']}/{e['id']}.mp4",
        })
    return {
        "type": "recordings",
        "count": len(recordings),
        "results": recordings,
    }


# ---------------------------------------------------------------------------
# Shared Users
# ---------------------------------------------------------------------------

def list_shared_users():
    return {"type": "shared_users", "count": len(_shared_users_store), "results": _shared_users_store}


def get_shared_user(user_id: int):
    for u in _shared_users_store:
        if u["user_id"] == user_id:
            return {"type": "shared_user", "shared_user": u}
    return {"error": f"User {user_id} not found"}


# ---------------------------------------------------------------------------
# Chime Settings
# ---------------------------------------------------------------------------

def get_chime_settings(device_id: int):
    device, category = _find_device(device_id)
    if not device:
        return {"error": f"Device {device_id} not found"}
    if category != "chimes":
        return {"error": f"Device {device_id} is not a chime"}
    return {"type": "chime_settings", "settings": device.get("settings", {})}


def link_chime_to_doorbell(chime_id: int, doorbell_id: int):
    chime, category = _find_device(chime_id)
    if not chime:
        return {"error": f"Device {chime_id} not found"}
    if category != "chimes":
        return {"error": f"Device {chime_id} is not a chime"}
    doorbell, db_cat = _find_device(doorbell_id)
    if not doorbell:
        return {"error": f"Doorbell {doorbell_id} not found"}
    linked = chime.get("settings", {}).get("linked_doorbots", [])
    if doorbell_id not in linked:
        linked.append(doorbell_id)
        chime["settings"]["linked_doorbots"] = linked
    return {"type": "chime_settings", "settings": chime["settings"]}


def unlink_chime_from_doorbell(chime_id: int, doorbell_id: int):
    chime, category = _find_device(chime_id)
    if not chime:
        return {"error": f"Device {chime_id} not found"}
    if category != "chimes":
        return {"error": f"Device {chime_id} is not a chime"}
    linked = chime.get("settings", {}).get("linked_doorbots", [])
    if doorbell_id in linked:
        linked.remove(doorbell_id)
        chime["settings"]["linked_doorbots"] = linked
    return {"type": "chime_settings", "settings": chime["settings"]}


# ---------------------------------------------------------------------------
# Motion Zones
# ---------------------------------------------------------------------------

def list_motion_zones(device_id: int):
    device, _ = _find_device(device_id)
    if not device:
        return {"error": f"Device {device_id} not found"}
    zones = [z for z in _motion_zones_store if z["device_id"] == device_id]
    return {"type": "motion_zones", "count": len(zones), "results": zones}


# ---------------------------------------------------------------------------
# Notification Preferences
# ---------------------------------------------------------------------------

def list_notification_prefs():
    return {"type": "notification_prefs", "count": len(_notification_prefs_store), "results": _notification_prefs_store}


def get_notification_pref(device_id: int):
    for p in _notification_prefs_store:
        if p["device_id"] == device_id:
            return {"type": "notification_pref", "notification_pref": p}
    return {"error": f"Notification preferences for device {device_id} not found"}


def update_notification_pref(device_id: int, data: dict):
    for i, p in enumerate(_notification_prefs_store):
        if p["device_id"] == device_id:
            updatable = {"motion_alerts", "ding_alerts", "person_alerts", "package_alerts"}
            for k, v in data.items():
                if k in updatable:
                    _notification_prefs_store[i][k] = v
            return {"type": "notification_pref", "notification_pref": _notification_prefs_store[i]}
    return {"error": f"Notification preferences for device {device_id} not found"}


# ---------------------------------------------------------------------------
# Siren Control
# ---------------------------------------------------------------------------

def activate_siren(device_id: int, duration_seconds: int = 30):
    device, category = _find_device(device_id)
    if not device:
        return {"error": f"Device {device_id} not found"}
    if "siren_status" not in device:
        return {"error": f"Device {device_id} does not have a siren"}
    device["siren_status"]["seconds_remaining"] = duration_seconds
    return {"type": "siren", "device_id": device_id, "siren_status": device["siren_status"]}


def deactivate_siren(device_id: int):
    device, category = _find_device(device_id)
    if not device:
        return {"error": f"Device {device_id} not found"}
    if "siren_status" not in device:
        return {"error": f"Device {device_id} does not have a siren"}
    device["siren_status"]["seconds_remaining"] = 0
    return {"type": "siren", "device_id": device_id, "siren_status": device["siren_status"]}


# ---------------------------------------------------------------------------
# Floodlight Control
# ---------------------------------------------------------------------------

def toggle_floodlight(device_id: int, on: bool):
    device, category = _find_device(device_id)
    if not device:
        return {"error": f"Device {device_id} not found"}
    if "floodlight_status" not in device:
        return {"error": f"Device {device_id} does not have a floodlight"}
    device["floodlight_status"]["on"] = on
    return {"type": "floodlight", "device_id": device_id, "floodlight_status": device["floodlight_status"]}
