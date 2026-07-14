"""FastAPI server wrapping whatsapp_data module as REST endpoints.

Loosely mirrors the WhatsApp Cloud API (Graph v17.0) surface.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

import whatsapp_data
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

app = FastAPI(title="WhatsApp Cloud API (Mock)", version="v17.0")
install_tracker(app)
install_admin_plane(app, store=whatsapp_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Business / phone numbers ---

@app.get("/v17.0/business")
def get_business():
    return whatsapp_data.get_business()


# --- Contacts ---

@app.get("/v17.0/contacts")
def list_contacts(opted_in_only: bool = False):
    return whatsapp_data.list_contacts(opted_in_only=opted_in_only)


@app.get("/v17.0/contacts/{wa_id}")
def get_contact(wa_id: str):
    result = whatsapp_data.get_contact(wa_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Templates ---

@app.get("/v17.0/message_templates")
def list_templates(status: Optional[str] = None):
    return whatsapp_data.list_templates(status=status)


@app.get("/v17.0/message_templates/{name}")
def get_template(name: str):
    result = whatsapp_data.get_template(name)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Conversations / messages ---

@app.get("/v17.0/conversations")
def list_conversations(wa_id: Optional[str] = None):
    return whatsapp_data.list_conversations(wa_id=wa_id)


@app.get("/v17.0/messages")
def list_messages(
    conversation_id: Optional[str] = None,
    wa_id: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
):
    return whatsapp_data.list_messages(conversation_id=conversation_id, wa_id=wa_id, limit=limit)


class TextMessage(BaseModel):
    body: str


class TemplateLanguage(BaseModel):
    code: str = "en_US"


class TemplateBlock(BaseModel):
    name: str
    language: Optional[TemplateLanguage] = None
    components: Optional[List[Dict[str, Any]]] = None


class SendMessageBody(BaseModel):
    messaging_product: str = "whatsapp"
    to: str
    type: str  # "text" or "template"
    text: Optional[TextMessage] = None
    template: Optional[TemplateBlock] = None


@app.post("/v17.0/messages")
def send_message(body: SendMessageBody):
    if body.type == "text":
        if not body.text:
            return JSONResponse(status_code=400, content={"error": "text body required"})
        result = whatsapp_data.send_text(body.to, body.text.body)
    elif body.type == "template":
        if not body.template:
            return JSONResponse(status_code=400, content={"error": "template body required"})
        result = whatsapp_data.send_template(
            body.to,
            body.template.name,
            components=body.template.components,
        )
    else:
        return JSONResponse(status_code=400, content={"error": f"Unsupported type: {body.type}"})
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class ReadStatusBody(BaseModel):
    messaging_product: str = "whatsapp"
    status: str = "read"
    message_id: str


@app.post("/v17.0/messages/status")
def mark_read(body: ReadStatusBody):
    result = whatsapp_data.mark_read(body.message_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
