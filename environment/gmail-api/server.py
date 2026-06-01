"""FastAPI server wrapping gmail_data module as REST endpoints.

Mirrors the Gmail API v1 (gmail/v1/users/{userId}) surface for a single user.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

import gmail_data
try:
    from tracking_middleware import install_tracker
except ModuleNotFoundError:  # standalone run without the shared module on sys.path
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

app = FastAPI(title="Gmail API (Mock)", version="v1")
install_tracker(app)


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Profile ---

@app.get("/gmail/v1/users/me/profile")
def get_profile():
    return gmail_data.get_profile()


# --- Labels ---

@app.get("/gmail/v1/users/me/labels")
def list_labels():
    return gmail_data.list_labels()


@app.get("/gmail/v1/users/me/labels/{label_id}")
def get_label(label_id: str):
    result = gmail_data.get_label(label_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class LabelCreateBody(BaseModel):
    name: str


@app.post("/gmail/v1/users/me/labels", status_code=201)
def create_label(body: LabelCreateBody):
    result = gmail_data.create_label(body.name)
    if "error" in result:
        return JSONResponse(status_code=409, content=result)
    return result


# --- Messages ---

@app.get("/gmail/v1/users/me/messages")
def list_messages(
    q: str = "",
    maxResults: int = Query(25, ge=1, le=500),
    labelIds: Optional[List[str]] = Query(None),
):
    return gmail_data.list_messages(query=q, max_results=maxResults, label_ids=labelIds or [])


@app.get("/gmail/v1/users/me/messages/{message_id}")
def get_message(message_id: str, format: str = "full"):
    result = gmail_data.get_message(message_id, fmt=format)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class SendBody(BaseModel):
    to: str
    subject: str
    body: str
    cc: Optional[str] = ""
    threadId: Optional[str] = None
    fromAddress: Optional[str] = None


@app.post("/gmail/v1/users/me/messages/send", status_code=201)
def send_message(body: SendBody):
    return gmail_data.send_message(
        to_addr=body.to, subject=body.subject, body=body.body,
        cc=body.cc, thread_id=body.threadId, from_addr=body.fromAddress,
    )


class ModifyBody(BaseModel):
    addLabelIds: Optional[List[str]] = None
    removeLabelIds: Optional[List[str]] = None


@app.post("/gmail/v1/users/me/messages/{message_id}/modify")
def modify_message(message_id: str, body: ModifyBody):
    result = gmail_data.modify_message(message_id, add_labels=body.addLabelIds, remove_labels=body.removeLabelIds)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/gmail/v1/users/me/messages/{message_id}/trash")
def trash_message(message_id: str):
    result = gmail_data.trash_message(message_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/gmail/v1/users/me/messages/{message_id}")
def delete_message(message_id: str):
    result = gmail_data.delete_message(message_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Threads ---

@app.get("/gmail/v1/users/me/threads")
def list_threads(q: str = ""):
    return gmail_data.list_threads(query=q)


@app.get("/gmail/v1/users/me/threads/{thread_id}")
def get_thread(thread_id: str):
    result = gmail_data.get_thread(thread_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Drafts ---

@app.get("/gmail/v1/users/me/drafts")
def list_drafts():
    return gmail_data.list_drafts()


@app.get("/gmail/v1/users/me/drafts/{draft_id}")
def get_draft(draft_id: str):
    result = gmail_data.get_draft(draft_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class DraftCreateBody(BaseModel):
    to: str
    subject: str
    body: str
    cc: Optional[str] = ""
    threadId: Optional[str] = None


@app.post("/gmail/v1/users/me/drafts", status_code=201)
def create_draft(body: DraftCreateBody):
    return gmail_data.create_draft(
        to_addr=body.to, subject=body.subject, body=body.body,
        cc=body.cc, thread_id=body.threadId,
    )


@app.post("/gmail/v1/users/me/drafts/{draft_id}/send")
def send_draft(draft_id: str):
    result = gmail_data.send_draft(draft_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
