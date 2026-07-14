"""FastAPI server wrapping mailchimp_data module as REST endpoints.

Implements a subset of the Mailchimp Marketing API. Routes live under /3.0/...
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import mailchimp_data
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

app = FastAPI(title="Mailchimp Marketing API (Mock)", version="3.0")
install_tracker(app)
install_admin_plane(app, store=mailchimp_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Lists / audiences ---

@app.get("/3.0/lists")
def list_lists():
    return mailchimp_data.list_lists()


@app.get("/3.0/lists/{list_id}")
def get_list(list_id: str):
    result = mailchimp_data.get_list(list_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Members ---

@app.get("/3.0/lists/{list_id}/members")
def list_members(list_id: str, status: Optional[str] = None):
    result = mailchimp_data.list_members(list_id, status=status)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class MemberCreateBody(BaseModel):
    email_address: str
    status: str = "subscribed"
    full_name: Optional[str] = ""
    member_rating: Optional[int] = 0


@app.post("/3.0/lists/{list_id}/members", status_code=201)
def create_member(list_id: str, body: MemberCreateBody):
    result = mailchimp_data.create_member(
        list_id,
        email_address=body.email_address,
        status=body.status,
        full_name=body.full_name or "",
        member_rating=body.member_rating or 0,
    )
    if "error" in result:
        code = 404 if "List" in result["error"] else 400
        return JSONResponse(status_code=code, content=result)
    return result


@app.get("/3.0/lists/{list_id}/members/{subscriber_hash}")
def get_member(list_id: str, subscriber_hash: str):
    result = mailchimp_data.get_member(list_id, subscriber_hash)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class MemberPatchBody(BaseModel):
    status: Optional[str] = None
    full_name: Optional[str] = None
    member_rating: Optional[int] = None


@app.patch("/3.0/lists/{list_id}/members/{subscriber_hash}")
def update_member(list_id: str, subscriber_hash: str, body: MemberPatchBody):
    result = mailchimp_data.update_member(
        list_id, subscriber_hash,
        status=body.status, full_name=body.full_name, member_rating=body.member_rating,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Campaigns ---

@app.get("/3.0/campaigns")
def list_campaigns(status: Optional[str] = None):
    return mailchimp_data.list_campaigns(status=status)


class CampaignRecipients(BaseModel):
    list_id: str


class CampaignSettings(BaseModel):
    subject_line: str
    from_name: str
    reply_to: str
    title: Optional[str] = ""


class CampaignCreateBody(BaseModel):
    type: str = "regular"
    recipients: CampaignRecipients
    settings: CampaignSettings


@app.post("/3.0/campaigns", status_code=201)
def create_campaign(body: CampaignCreateBody):
    result = mailchimp_data.create_campaign(
        list_id=body.recipients.list_id,
        subject_line=body.settings.subject_line,
        from_name=body.settings.from_name,
        reply_to=body.settings.reply_to,
        title=body.settings.title or "",
        type_=body.type,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/3.0/campaigns/{campaign_id}")
def get_campaign(campaign_id: str):
    result = mailchimp_data.get_campaign(campaign_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/3.0/campaigns/{campaign_id}/actions/send", status_code=204)
def send_campaign(campaign_id: str):
    result = mailchimp_data.send_campaign(campaign_id)
    if "error" in result:
        code = 404 if "not found" in result["error"] else 400
        return JSONResponse(status_code=code, content=result)
    # Mailchimp returns 204 No Content; surface details via 200 for the mock.
    return JSONResponse(status_code=200, content=result)


# --- Reports ---

@app.get("/3.0/reports/{campaign_id}")
def get_report(campaign_id: str):
    result = mailchimp_data.get_report(campaign_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
