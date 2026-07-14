"""FastAPI server wrapping mailgun_data module as REST endpoints.

Mirrors a subset of the Mailgun Email API (api.mailgun.net/v3): sending
messages, querying delivery events, total stats, and mailing-list members.
Like the real Mailgun API, message sending posts the message fields in the
request body (here as JSON, using the same field names as the real API).
"""

from fastapi import FastAPI, Query, Body
from fastapi.responses import JSONResponse
from typing import Optional

import mailgun_data
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

app = FastAPI(title="Mailgun API (Mock)", version="v3")
install_tracker(app)
install_admin_plane(app, store=mailgun_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Messages (send) ---

@app.post("/v3/{domain}/messages")
def send_message(
    domain: str,
    sender: str = Body(..., alias="from", embed=True),
    to: str = Body(..., embed=True),
    subject: str = Body("", embed=True),
    text: str = Body("", embed=True),
):
    result = mailgun_data.send_message(domain, sender=sender, to=to, subject=subject, text=text)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Events ---

@app.get("/v3/{domain}/events")
def get_events(
    domain: str,
    event: Optional[str] = None,
    recipient: Optional[str] = None,
    limit: int = Query(300, ge=1, le=300),
):
    return mailgun_data.get_events(domain, event=event, recipient=recipient, limit=limit)


# --- Stats ---

@app.get("/v3/{domain}/stats/total")
def get_stats_total(domain: str, event: Optional[str] = None):
    return mailgun_data.get_stats_total(domain, event=event)


# --- Mailing list members ---

@app.get("/v3/lists/{address}/members")
def list_members(address: str, subscribed: Optional[bool] = None):
    result = mailgun_data.list_members(address, subscribed=subscribed)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
