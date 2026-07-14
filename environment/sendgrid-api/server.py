"""FastAPI server wrapping sendgrid_data module as REST endpoints.

Mirrors a subset of the SendGrid v3 API: mail send, templates, marketing
contacts, lists and email stats. Base path: /v3
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any

import sendgrid_data
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

app = FastAPI(title="SendGrid API (Mock)", version="v3")
install_tracker(app)
install_admin_plane(app, store=sendgrid_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Mail send ---

class EmailAddress(BaseModel):
    email: str
    name: Optional[str] = None


class Personalization(BaseModel):
    to: List[EmailAddress]
    subject: Optional[str] = None
    dynamic_template_data: Optional[Dict[str, Any]] = None


class MailSendBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    personalizations: List[Personalization]
    from_: Optional[EmailAddress] = Field(default=None, alias="from")
    subject: Optional[str] = None
    content: Optional[List[Dict[str, Any]]] = None
    template_id: Optional[str] = None


@app.post("/v3/mail/send", status_code=202)
def send_mail(body: MailSendBody):
    from_email = body.from_.email if body.from_ else None
    result = sendgrid_data.send_mail(
        personalizations=[p.model_dump() for p in body.personalizations],
        from_email=from_email,
        subject=body.subject,
        content=body.content,
        template_id=body.template_id,
    )
    if result.get("status") == 400 or "errors" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Templates ---

@app.get("/v3/templates")
def list_templates(generations: Optional[str] = None):
    return sendgrid_data.list_templates(generation=generations)


@app.get("/v3/templates/{template_id}")
def get_template(template_id: str):
    result = sendgrid_data.get_template(template_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class TemplateCreateBody(BaseModel):
    name: str
    generation: str = "dynamic"
    subject: Optional[str] = ""
    html_content: Optional[str] = ""


@app.post("/v3/templates", status_code=201)
def create_template(body: TemplateCreateBody):
    return sendgrid_data.create_template(
        name=body.name,
        generation=body.generation,
        subject=body.subject,
        html_content=body.html_content,
    )


# --- Marketing contacts ---

@app.get("/v3/marketing/contacts")
def list_contacts(email: Optional[str] = None):
    return sendgrid_data.list_contacts(email=email)


class ContactInput(BaseModel):
    email: str
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    country: Optional[str] = ""


class ContactsUpsertBody(BaseModel):
    contacts: List[ContactInput]
    list_ids: Optional[List[str]] = None


@app.post("/v3/marketing/contacts", status_code=202)
def upsert_contacts(body: ContactsUpsertBody):
    return sendgrid_data.upsert_contacts(
        contacts=[c.model_dump() for c in body.contacts],
        list_ids=body.list_ids,
    )


# --- Lists ---

@app.get("/v3/marketing/lists")
def list_lists():
    return sendgrid_data.list_lists()


# --- Stats ---

@app.get("/v3/stats")
def get_stats(start_date: str = Query(...), end_date: Optional[str] = None):
    return sendgrid_data.get_stats(start_date=start_date, end_date=end_date)
