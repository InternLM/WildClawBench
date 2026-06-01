"""FastAPI server wrapping outlook_data as REST endpoints.

Mirrors a subset of the Microsoft Graph v1.0 API for the signed-in user's
mailbox and calendar: messages, sendMail, events, and contacts. Collections
are wrapped as {"value": [...]} like the real Graph API.
"""

from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from typing import Optional

import outlook_data
try:
    from tracking_middleware import install_tracker
except ModuleNotFoundError:  # standalone run without the shared module on sys.path
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

app = FastAPI(title="Outlook API (Mock)", version="v1.0")
install_tracker(app)


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Mail messages ---

@app.get("/v1.0/me/messages")
def list_messages(isRead: Optional[bool] = None):
    return outlook_data.list_messages(is_read=isRead)


@app.get("/v1.0/me/messages/{message_id}")
def get_message(message_id: str):
    result = outlook_data.get_message(message_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/v1.0/me/sendMail", status_code=202)
def send_mail(body: dict = Body(...)):
    message = body.get("message") or {}
    subject = message.get("subject")
    body_obj = message.get("body") or {}
    content = body_obj.get("content")
    content_type = body_obj.get("contentType", "HTML")
    recipients = [
        r.get("emailAddress", {}).get("address")
        for r in message.get("toRecipients", [])
        if r.get("emailAddress", {}).get("address")
    ]
    result = outlook_data.send_mail(
        subject=subject, content=content,
        to_recipients=recipients, content_type=content_type,
    )
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Calendar events ---

@app.get("/v1.0/me/events")
def list_events():
    return outlook_data.list_events()


# --- Contacts ---

@app.get("/v1.0/me/contacts")
def list_contacts():
    return outlook_data.list_contacts()
