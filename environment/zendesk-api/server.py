"""FastAPI server wrapping zendesk_data module as REST endpoints.

Mirrors a subset of the Zendesk Support API v2. Base path: /api/v2
Create/update use the Zendesk {"ticket": {...}} body shape; updates may carry an
embedded {"comment": {...}} to add a comment in the same call.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

import zendesk_data
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

app = FastAPI(title="Zendesk Support API (Mock)", version="v2")
install_tracker(app)
install_admin_plane(app, store=zendesk_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Tickets ---

@app.get("/api/v2/tickets")
def list_tickets(status: Optional[str] = None, priority: Optional[str] = None,
                 assignee_id: Optional[int] = None):
    return zendesk_data.list_tickets(status=status, priority=priority, assignee_id=assignee_id)


@app.get("/api/v2/tickets/{ticket_id}")
def get_ticket(ticket_id: int):
    result = zendesk_data.get_ticket(ticket_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class TicketComment(BaseModel):
    body: str
    public: Optional[bool] = True
    author_id: Optional[int] = None


class TicketCreate(BaseModel):
    subject: str
    description: Optional[str] = None
    priority: Optional[str] = "normal"
    type: Optional[str] = "question"
    requester_id: Optional[int] = None
    assignee_id: Optional[int] = None
    organization_id: Optional[int] = None
    tags: Optional[List[str]] = None
    comment: Optional[TicketComment] = None


class TicketCreateBody(BaseModel):
    ticket: TicketCreate


@app.post("/api/v2/tickets", status_code=201)
def create_ticket(body: TicketCreateBody):
    t = body.ticket
    result = zendesk_data.create_ticket(
        subject=t.subject, description=t.description, priority=t.priority,
        ticket_type=t.type, requester_id=t.requester_id, assignee_id=t.assignee_id,
        organization_id=t.organization_id, tags=t.tags,
        comment_body=t.comment.body if t.comment else None,
    )
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class TicketUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_id: Optional[int] = None
    type: Optional[str] = None
    tags: Optional[List[str]] = None
    comment: Optional[TicketComment] = None


class TicketUpdateBody(BaseModel):
    ticket: TicketUpdate


@app.put("/api/v2/tickets/{ticket_id}")
def update_ticket(ticket_id: int, body: TicketUpdateBody):
    t = body.ticket
    result = zendesk_data.update_ticket(
        ticket_id, status=t.status, priority=t.priority, assignee_id=t.assignee_id,
        ticket_type=t.type, tags=t.tags,
        comment_body=t.comment.body if t.comment else None,
        comment_public=t.comment.public if t.comment else True,
        comment_author_id=t.comment.author_id if t.comment else None,
    )
    if "error" in result:
        status = 404 if "not found" in result["error"] else 400
        return JSONResponse(status_code=status, content=result)
    return result


# --- Comments ---

@app.get("/api/v2/tickets/{ticket_id}/comments")
def list_comments(ticket_id: int):
    result = zendesk_data.list_comments(ticket_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class CommentCreate(BaseModel):
    body: str
    public: Optional[bool] = True
    author_id: Optional[int] = None


class CommentCreateBody(BaseModel):
    comment: CommentCreate


@app.post("/api/v2/tickets/{ticket_id}/comments", status_code=201)
def create_comment(ticket_id: int, body: CommentCreateBody):
    c = body.comment
    result = zendesk_data.create_comment(ticket_id, c.body, author_id=c.author_id, public=c.public)
    if "error" in result:
        status = 404 if "not found" in result["error"] else 400
        return JSONResponse(status_code=status, content=result)
    return result


# --- Users ---

@app.get("/api/v2/users")
def list_users(role: Optional[str] = None):
    return zendesk_data.list_users(role=role)


@app.get("/api/v2/users/{user_id}")
def get_user(user_id: int):
    result = zendesk_data.get_user(user_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Organizations ---

@app.get("/api/v2/organizations")
def list_organizations():
    return zendesk_data.list_organizations()
