"""FastAPI server wrapping ring_data module as REST endpoints."""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import ring_data
try:
    from tracking_middleware import install_tracker
    from admin_plane import install_admin_plane
except ModuleNotFoundError as _shared_plane_err:  # standalone run without the shared module on sys.path
    import logging as _logging
    _logging.error("SHARED PLANE MISSING - audit + admin disabled: %s", _shared_plane_err)
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

    def install_admin_plane(app, store=None, one_shot_registry=None):
        return None

app = FastAPI(title="Ring API (Mock)", version="1.0.0")
install_tracker(app)
install_admin_plane(app, store=ring_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Devices ---

@app.get("/clients_api/ring_devices")
def list_devices():
    return ring_data.list_devices()


@app.get("/clients_api/doorbots/{device_id}")
def get_device(device_id: int):
    result = ring_data.get_device(device_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/clients_api/doorbots/{device_id}/health")
def get_device_health(device_id: int):
    result = ring_data.get_device_health(device_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class DeviceSettingsUpdateBody(BaseModel):
    motion_sensitivity: Optional[int] = None
    motion_detection_enabled: Optional[bool] = None
    people_detection_enabled: Optional[bool] = None
    package_detection_enabled: Optional[bool] = None
    led_status: Optional[str] = None
    light_schedule_enabled: Optional[bool] = None
    light_on_duration_seconds: Optional[int] = None


@app.put("/clients_api/doorbots/{device_id}/settings")
def update_device_settings(device_id: int, body: DeviceSettingsUpdateBody):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    result = ring_data.update_device_settings(device_id, data)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Locations ---

@app.get("/clients_api/locations/{location_id}")
def get_location(location_id: str):
    result = ring_data.get_location(location_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/clients_api/locations/{location_id}/devices")
def list_location_devices(location_id: str):
    result = ring_data.list_location_devices(location_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/clients_api/locations/{location_id}/mode")
def get_location_mode(location_id: str):
    result = ring_data.get_location_mode(location_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class ModeUpdateBody(BaseModel):
    mode: str


@app.put("/clients_api/locations/{location_id}/mode")
def set_location_mode(location_id: str, body: ModeUpdateBody):
    result = ring_data.set_location_mode(location_id, body.mode)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Active Dings ---

@app.get("/clients_api/dings/active")
def list_active_dings():
    return ring_data.list_active_dings()


# --- Event History ---

@app.get("/clients_api/doorbots/{device_id}/history")
def list_device_events(
    device_id: int,
    kind: Optional[str] = Query(default=None),
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return ring_data.list_device_events(
        device_id=device_id, kind=kind, date_from=date_from,
        date_to=date_to, limit=limit, offset=offset,
    )


@app.get("/clients_api/dings/{event_id}")
def get_event(event_id: int):
    result = ring_data.get_event(event_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/clients_api/dings/{event_id}/recording")
def get_event_recording(event_id: int):
    result = ring_data.get_event_recording(event_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Recordings ---

@app.get("/clients_api/doorbots/{device_id}/recordings")
def list_recordings(
    device_id: int,
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
):
    return ring_data.list_recordings(device_id=device_id, date_from=date_from, date_to=date_to)


# --- Shared Users ---

@app.get("/clients_api/locations/{location_id}/users")
def list_shared_users(location_id: str):
    if location_id != "loc_martinez_001":
        return JSONResponse(status_code=404, content={"error": f"Location {location_id} not found"})
    return ring_data.list_shared_users()


@app.get("/clients_api/locations/{location_id}/users/{user_id}")
def get_shared_user(location_id: str, user_id: int):
    if location_id != "loc_martinez_001":
        return JSONResponse(status_code=404, content={"error": f"Location {location_id} not found"})
    result = ring_data.get_shared_user(user_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Chime Settings ---

@app.get("/clients_api/chimes/{device_id}/settings")
def get_chime_settings(device_id: int):
    result = ring_data.get_chime_settings(device_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class ChimeLinkBody(BaseModel):
    doorbell_id: int


@app.put("/clients_api/chimes/{device_id}/link")
def link_chime_to_doorbell(device_id: int, body: ChimeLinkBody):
    result = ring_data.link_chime_to_doorbell(device_id, body.doorbell_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.put("/clients_api/chimes/{device_id}/unlink")
def unlink_chime_from_doorbell(device_id: int, body: ChimeLinkBody):
    result = ring_data.unlink_chime_from_doorbell(device_id, body.doorbell_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Motion Zones ---

@app.get("/clients_api/doorbots/{device_id}/motion_zones")
def list_motion_zones(device_id: int):
    result = ring_data.list_motion_zones(device_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Notification Preferences ---

@app.get("/clients_api/notifications")
def list_notification_prefs():
    return ring_data.list_notification_prefs()


@app.get("/clients_api/notifications/{device_id}")
def get_notification_pref(device_id: int):
    result = ring_data.get_notification_pref(device_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class NotificationPrefUpdateBody(BaseModel):
    motion_alerts: Optional[bool] = None
    ding_alerts: Optional[bool] = None
    person_alerts: Optional[bool] = None
    package_alerts: Optional[bool] = None


@app.put("/clients_api/notifications/{device_id}")
def update_notification_pref(device_id: int, body: NotificationPrefUpdateBody):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    result = ring_data.update_notification_pref(device_id, data)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Siren ---

class SirenBody(BaseModel):
    duration_seconds: Optional[int] = 30


@app.post("/clients_api/doorbots/{device_id}/siren_on")
def activate_siren(device_id: int, body: SirenBody = SirenBody()):
    result = ring_data.activate_siren(device_id, body.duration_seconds)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/clients_api/doorbots/{device_id}/siren_off")
def deactivate_siren(device_id: int):
    result = ring_data.deactivate_siren(device_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Floodlight ---

class FloodlightBody(BaseModel):
    on: bool


@app.put("/clients_api/doorbots/{device_id}/floodlight_light_on")
def toggle_floodlight(device_id: int, body: FloodlightBody):
    result = ring_data.toggle_floodlight(device_id, body.on)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
