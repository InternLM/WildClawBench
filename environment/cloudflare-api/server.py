"""FastAPI server wrapping cloudflare_data module as REST endpoints.

Mirrors a subset of the Cloudflare API v4. Base path: /client/v4
All responses use the Cloudflare envelope:
    {"success": bool, "errors": [...], "messages": [...], "result": ...}
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import cloudflare_data
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

app = FastAPI(title="Cloudflare API (Mock)", version="v4")
install_tracker(app)
install_admin_plane(app, store=cloudflare_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


def _respond(result):
    """Return a Cloudflare envelope, mapping `_status` to the HTTP status code."""
    if not result.get("success", True):
        status = result.pop("_status", 400)
        return JSONResponse(status_code=status, content=result)
    return result


# --- Zones ---

@app.get("/client/v4/zones")
def list_zones(name: Optional[str] = None, status: Optional[str] = None):
    return _respond(cloudflare_data.list_zones(name=name, status=status))


@app.get("/client/v4/zones/{zone_id}")
def get_zone(zone_id: str):
    return _respond(cloudflare_data.get_zone(zone_id))


# --- DNS records ---

@app.get("/client/v4/zones/{zone_id}/dns_records")
def list_dns_records(zone_id: str, type: Optional[str] = None, name: Optional[str] = None):
    return _respond(cloudflare_data.list_dns_records(zone_id, type=type, name=name))


@app.get("/client/v4/zones/{zone_id}/dns_records/{record_id}")
def get_dns_record(zone_id: str, record_id: str):
    return _respond(cloudflare_data.get_dns_record(zone_id, record_id))


class DNSRecordCreateBody(BaseModel):
    type: str
    name: str
    content: str
    ttl: Optional[int] = 1
    proxied: Optional[bool] = False
    priority: Optional[int] = 0


@app.post("/client/v4/zones/{zone_id}/dns_records", status_code=200)
def create_dns_record(zone_id: str, body: DNSRecordCreateBody):
    return _respond(cloudflare_data.create_dns_record(
        zone_id, type=body.type, name=body.name, content=body.content,
        ttl=body.ttl, proxied=body.proxied, priority=body.priority,
    ))


class DNSRecordUpdateBody(BaseModel):
    type: Optional[str] = None
    name: Optional[str] = None
    content: Optional[str] = None
    ttl: Optional[int] = None
    proxied: Optional[bool] = None
    priority: Optional[int] = None


@app.put("/client/v4/zones/{zone_id}/dns_records/{record_id}")
def update_dns_record(zone_id: str, record_id: str, body: DNSRecordUpdateBody):
    return _respond(cloudflare_data.update_dns_record(
        zone_id, record_id, type=body.type, name=body.name, content=body.content,
        ttl=body.ttl, proxied=body.proxied, priority=body.priority,
    ))


@app.delete("/client/v4/zones/{zone_id}/dns_records/{record_id}")
def delete_dns_record(zone_id: str, record_id: str):
    return _respond(cloudflare_data.delete_dns_record(zone_id, record_id))


# --- Firewall rules ---

@app.get("/client/v4/zones/{zone_id}/firewall/rules")
def list_firewall_rules(zone_id: str):
    return _respond(cloudflare_data.list_firewall_rules(zone_id))
