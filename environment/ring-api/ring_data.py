"""Data access module for Ring API simulation."""

import csv
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_int, opt_str, strict_int)
_store = get_store("ring-api")
_API = "ring-api"


def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _load_json(filename):
    with open(DATA_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _coerce_events(rows):
    out = []
    for r in rows:
        out.append({
            "id": strict_int(r, "id"),
            "doorbot_id": strict_int(r, "doorbot_id"),
            "device_id": r["device_id"],
            "kind": r["kind"],
            "created_at": r["created_at"],
            "answered": r["answered"].lower() == "true",
            "favorite": r["favorite"].lower() == "true",
            "recording": {"status": r["recording_status"]},
            "snapshot_url": r["snapshot_url"],
            "duration_seconds": opt_int(r, "duration_seconds", default=None),
            "cv_properties": opt_str(r, "cv_properties", default="") or None,
        })
    return out


def _coerce_shared_users(rows):
    out = []
    for r in rows:
        out.append({
            "user_id": strict_int(r, "user_id"),
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
            "device_id": strict_int(r, "device_id"),
            "zone_id": r["zone_id"],
            "zone_name": r["zone_name"],
            "sensitivity": strict_int(r, "sensitivity"),
            "enabled": r["enabled"].lower() == "true",
            "coordinates": r["coordinates"],
        })
    return out


def _coerce_notification_prefs(rows):
    out = []
    for r in rows:
        device_id = strict_int(r, "device_id")
        channel = r.get("channel") or "push"
        out.append({
            "_pk": f"{device_id}/{channel}",
            "device_id": device_id,
            "channel": channel,
            "motion_alerts": r["motion_alerts"].lower() == "true" if r["motion_alerts"] else None,
            "ding_alerts": r["ding_alerts"].lower() == "true" if r["ding_alerts"] else None,
            "person_alerts": r["person_alerts"].lower() == "true" if r["person_alerts"] else None,
            "package_alerts": r["package_alerts"].lower() == "true" if r["package_alerts"] else None,
        })
    return out


# devices is a nested dict-of-lists ({"doorbots":[..], "stickup_cams":[..], "chimes":[..]})
# kept as a Document because the shape isn't a flat list-of-records.
_store.register_document("devices", initial_loader=lambda: _load_json("devices.json"))
_store.register_document("location", initial_loader=lambda: _load_json("location.json"))
_store.register_document("active_dings", initial_loader=lambda: _load_json("active_dings.json"))

_store.register("events", primary_key="id",
                initial_loader=lambda: _coerce_events(_load("events.json", "events")))
_store.register("shared_users", primary_key="user_id",
                initial_loader=lambda: _coerce_shared_users(_load("shared_users.json", "shared_users")))
# motion_zones natural key (device_id, zone_id) -> synth composite pk
_store.register("motion_zones", primary_key="_pk",
                initial_loader=lambda: [
                    {**z, "_pk": f"{z['device_id']}@{z['zone_id']}"}
                    for z in _coerce_motion_zones(_load("motion_zones.json", "motion_zones"))])
_store.register("notification_prefs", primary_key="_pk",
                initial_loader=lambda: _coerce_notification_prefs(
                    _load("notification_prefs.json", "notification_prefs")))


def _devices(): return _store.document("devices").get()
def _location(): return _store.document("location").get()
def _active_dings(): return _store.document("active_dings").get()
def _events_rows(): return _store.table("events").rows()
def _shared_users_rows(): return _store.table("shared_users").rows()
def _motion_zones_rows(): return _store.table("motion_zones").rows()
def _notification_prefs_rows(): return [{k: v for k, v in r.items() if k != "_pk"} for r in _store.table("notification_prefs").rows()]


def _next_event_id():
    rows = _events_rows()
    if not rows:
        return 1
    return max(e["id"] for e in rows) + 1


def _all_devices():
    devices = []
    d = _devices()
    for dev in d.get("doorbots", []):
        devices.append({**dev, "device_type": "doorbot"})
    for dev in d.get("stickup_cams", []):
        devices.append({**dev, "device_type": "stickup_cam"})
    for dev in d.get("chimes", []):
        devices.append({**dev, "device_type": "chime"})
    return devices


def _find_device(device_id):
    d = _devices()
    for category in ["doorbots", "stickup_cams", "chimes"]:
        for dev in d.get(category, []):
            if dev["id"] == device_id:
                return dev, category
    return None, None


def _mutate_device(device_id, mutator):
    """Read devices doc, find device, apply mutator(device), write back. Returns (device, category) or (None, None)."""
    d = _devices()
    for category in ["doorbots", "stickup_cams", "chimes"]:
        for dev in d.get(category, []):
            if dev["id"] == device_id:
                mutator(dev)
                _store.document("devices").set(d)
                return dev, category
    return None, None


def list_devices():
    return _devices()


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
    updatable = {
        "motion_sensitivity", "motion_detection_enabled", "people_detection_enabled",
        "package_detection_enabled", "led_status", "light_schedule_enabled",
        "light_on_duration_seconds",
    }

    def _apply(device):
        settings = device.get("settings", {})
        for k, v in data.items():
            if k in updatable:
                settings[k] = v
            elif k == "led_status":
                device["led_status"] = v
        device["settings"] = settings

    device, category = _mutate_device(device_id, _apply)
    if not device:
        return {"error": f"Device {device_id} not found"}
    return {"type": "device", "device_type": category, "device": device}


def get_location(location_id: str):
    loc = _location()
    if location_id != loc["location_id"]:
        return {"error": f"Location {location_id} not found"}
    return {"type": "location", "location": loc}


def list_location_devices(location_id: str):
    loc = _location()
    if location_id != loc["location_id"]:
        return {"error": f"Location {location_id} not found"}
    return _devices()


def get_location_mode(location_id: str):
    loc = _location()
    if location_id != loc["location_id"]:
        return {"error": f"Location {location_id} not found"}
    return {"type": "mode", "mode": loc["mode"], "location_id": location_id}


def set_location_mode(location_id: str, mode: str):
    loc = _location()
    if location_id != loc["location_id"]:
        return {"error": f"Location {location_id} not found"}
    valid_modes = ["home", "away", "disarmed"]
    if mode not in valid_modes:
        return {"error": f"Invalid mode '{mode}'. Must be one of: {valid_modes}"}
    _store.document("location").merge({"mode": mode, "updated_at": _now()})
    return {"type": "mode", "mode": mode, "location_id": location_id}


def list_device_events(
    device_id: int,
    kind: str = None,
    date_from: str = None,
    date_to: str = None,
    limit: int = 20,
    offset: int = 0,
):
    results = [e for e in _events_rows() if e["doorbot_id"] == device_id]

    if kind:
        results = [e for e in results if e["kind"] == kind]
    if date_from:
        results = [e for e in results if e["created_at"] >= date_from]
    if date_to:
        results = [e for e in results if e["created_at"] <= date_to]

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
    e = _store.table("events").get(event_id)
    if e:
        return {"type": "event", "event": e}
    return {"error": f"Event {event_id} not found"}


def get_event_recording(event_id: int):
    e = _store.table("events").get(event_id)
    if not e:
        return {"error": f"Event {event_id} not found"}
    if e["recording"]["status"] != "ready":
        return {"error": f"Recording not available for event {event_id}"}
    location_id = _location()["location_id"]
    url = f"https://ring-recordings.s3.amazonaws.com/{location_id}/{e['device_id']}/{event_id}.mp4"
    return {"type": "recording", "event_id": event_id, "recording_url": url}


def list_active_dings():
    return _active_dings()


def list_recordings(device_id: int, date_from: str = None, date_to: str = None):
    events = [e for e in _events_rows()
              if e["doorbot_id"] == device_id and e["recording"]["status"] == "ready"]

    if date_from:
        events = [e for e in events if e["created_at"] >= date_from]
    if date_to:
        events = [e for e in events if e["created_at"] <= date_to]

    events = sorted(events, key=lambda x: x["created_at"], reverse=True)

    location_id = _location()["location_id"]
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


def list_shared_users():
    rows = _shared_users_rows()
    return {"type": "shared_users", "count": len(rows), "results": rows}


def get_shared_user(user_id: int):
    u = _store.table("shared_users").get(user_id)
    if u:
        return {"type": "shared_user", "shared_user": u}
    return {"error": f"User {user_id} not found"}


def get_chime_settings(device_id: int):
    device, category = _find_device(device_id)
    if not device:
        return {"error": f"Device {device_id} not found"}
    if category != "chimes":
        return {"error": f"Device {device_id} is not a chime"}
    return {"type": "chime_settings", "settings": device.get("settings", {})}


def link_chime_to_doorbell(chime_id: int, doorbell_id: int):
    doorbell, _ = _find_device(doorbell_id)
    if not doorbell:
        chime_check, _ = _find_device(chime_id)
        if not chime_check:
            return {"error": f"Device {chime_id} not found"}
        return {"error": f"Doorbell {doorbell_id} not found"}

    chime_check, chime_cat = _find_device(chime_id)
    if not chime_check:
        return {"error": f"Device {chime_id} not found"}
    if chime_cat != "chimes":
        return {"error": f"Device {chime_id} is not a chime"}

    def _apply(chime):
        linked = chime.get("settings", {}).get("linked_doorbots", [])
        if doorbell_id not in linked:
            linked.append(doorbell_id)
        chime.setdefault("settings", {})["linked_doorbots"] = linked

    chime, _ = _mutate_device(chime_id, _apply)
    return {"type": "chime_settings", "settings": (chime or {}).get("settings", {})}


def unlink_chime_from_doorbell(chime_id: int, doorbell_id: int):
    chime_check, chime_cat = _find_device(chime_id)
    if not chime_check:
        return {"error": f"Device {chime_id} not found"}
    if chime_cat != "chimes":
        return {"error": f"Device {chime_id} is not a chime"}

    def _apply(chime):
        linked = chime.get("settings", {}).get("linked_doorbots", [])
        if doorbell_id in linked:
            linked.remove(doorbell_id)
        chime.setdefault("settings", {})["linked_doorbots"] = linked

    chime, _ = _mutate_device(chime_id, _apply)
    return {"type": "chime_settings", "settings": (chime or {}).get("settings", {})}


def list_motion_zones(device_id: int):
    device, _ = _find_device(device_id)
    if not device:
        return {"error": f"Device {device_id} not found"}
    zones = [z for z in _motion_zones_rows() if z["device_id"] == device_id]
    public = [{k: v for k, v in z.items() if k != "_pk"} for z in zones]
    return {"type": "motion_zones", "count": len(public), "results": public}


def list_notification_prefs():
    rows = _notification_prefs_rows()
    return {"type": "notification_prefs", "count": len(rows), "results": rows}


def get_notification_pref(device_id: int, channel: str = "push"):
    pk = f"{device_id}/{channel}"
    p = _store.table("notification_prefs").get(pk)
    if p:
        return {"type": "notification_pref",
                "notification_pref": {k: v for k, v in p.items() if k != "_pk"}}
    return {"error": f"Notification preferences for device {device_id} not found"}


def update_notification_pref(device_id: int, data: dict, channel: str = "push"):
    pk = f"{device_id}/{channel}"
    p = _store.table("notification_prefs").get(pk)
    if not p:
        return {"error": f"Notification preferences for device {device_id} not found"}
    updatable = {"motion_alerts", "ding_alerts", "person_alerts", "package_alerts"}
    patch = {k: v for k, v in data.items() if k in updatable}
    if patch:
        _store.table("notification_prefs").patch(pk, patch)
    after = _store.table("notification_prefs").get(pk)
    return {"type": "notification_pref",
            "notification_pref": {k: v for k, v in after.items() if k != "_pk"}}


def activate_siren(device_id: int, duration_seconds: int = 30):
    def _apply(device):
        device.setdefault("siren_status", {})["seconds_remaining"] = duration_seconds

    pre_device, _ = _find_device(device_id)
    if not pre_device:
        return {"error": f"Device {device_id} not found"}
    if "siren_status" not in pre_device:
        return {"error": f"Device {device_id} does not have a siren"}
    device, _ = _mutate_device(device_id, _apply)
    return {"type": "siren", "device_id": device_id,
            "siren_status": (device or {}).get("siren_status", {})}


def deactivate_siren(device_id: int):
    pre_device, _ = _find_device(device_id)
    if not pre_device:
        return {"error": f"Device {device_id} not found"}
    if "siren_status" not in pre_device:
        return {"error": f"Device {device_id} does not have a siren"}

    def _apply(device):
        device.setdefault("siren_status", {})["seconds_remaining"] = 0

    device, _ = _mutate_device(device_id, _apply)
    return {"type": "siren", "device_id": device_id,
            "siren_status": (device or {}).get("siren_status", {})}


def toggle_floodlight(device_id: int, on: bool):
    pre_device, _ = _find_device(device_id)
    if not pre_device:
        return {"error": f"Device {device_id} not found"}
    if "floodlight_status" not in pre_device:
        return {"error": f"Device {device_id} does not have a floodlight"}

    def _apply(device):
        device.setdefault("floodlight_status", {})["on"] = on

    device, _ = _mutate_device(device_id, _apply)
    return {"type": "floodlight", "device_id": device_id,
            "floodlight_status": (device or {}).get("floodlight_status", {})}

_store.eager_load()
