"""FastAPI server wrapping intercom_data module as REST endpoints.

Implements a subset of the Intercom API: contacts, conversations,
conversation parts and companies.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import intercom_data
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

app = FastAPI(title="Intercom API (Mock)", version="2.11")
install_tracker(app)
install_admin_plane(app, store=intercom_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Contacts ---

@app.get("/contacts")
def list_contacts(role: Optional[str] = None):
    return intercom_data.list_contacts(role=role)


class ContactCreateBody(BaseModel):
    role: str = "user"
    name: Optional[str] = ""
    email: Optional[str] = None
    phone: Optional[str] = None
    company_id: Optional[str] = None


@app.post("/contacts", status_code=201)
def create_contact(body: ContactCreateBody):
    return intercom_data.create_contact(
        role=body.role, name=body.name or "", email=body.email,
        phone=body.phone, company_id=body.company_id,
    )


@app.get("/contacts/{contact_id}")
def get_contact(contact_id: str):
    result = intercom_data.get_contact(contact_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Conversations ---

@app.get("/conversations")
def list_conversations(state: Optional[str] = None):
    return intercom_data.list_conversations(state=state)


class ConversationCreateBody(BaseModel):
    contact_id: str
    body: str
    title: Optional[str] = ""


@app.post("/conversations", status_code=201)
def create_conversation(body: ConversationCreateBody):
    result = intercom_data.create_conversation(body.contact_id, body.body, title=body.title or "")
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: str):
    result = intercom_data.get_conversation(conversation_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class ReplyBody(BaseModel):
    body: str
    author_type: str = "admin"
    author_id: str = "admin-jonas"


@app.post("/conversations/{conversation_id}/reply")
def reply_conversation(conversation_id: str, body: ReplyBody):
    result = intercom_data.reply_conversation(
        conversation_id, body.body, author_type=body.author_type, author_id=body.author_id,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class PartBody(BaseModel):
    message_type: str
    body: Optional[str] = None
    author_id: str = "admin-jonas"
    assignee_id: Optional[str] = None


@app.post("/conversations/{conversation_id}/parts")
def add_part(conversation_id: str, body: PartBody):
    result = intercom_data.add_part(
        conversation_id,
        message_type=body.message_type,
        body=body.body,
        author_id=body.author_id,
        assignee_id=body.assignee_id,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Companies ---

@app.get("/companies")
def list_companies():
    return intercom_data.list_companies()


@app.get("/companies/{company_id}")
def get_company(company_id: str):
    result = intercom_data.get_company(company_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
