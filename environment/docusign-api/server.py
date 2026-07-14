"""FastAPI server wrapping docusign_data module as REST endpoints.

Mirrors a subset of the DocuSign eSignature REST API v2.1.
Routes are namespaced under /restapi/v2.1/accounts/{accountId}/...
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

import docusign_data
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

app = FastAPI(title="DocuSign eSignature API (Mock)", version="v2.1")
install_tracker(app)
install_admin_plane(app, store=docusign_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Envelopes ---

@app.get("/restapi/v2.1/accounts/{accountId}/envelopes")
def list_envelopes(accountId: str, status: Optional[str] = None):
    return docusign_data.list_envelopes(status=status)


class EnvelopeRecipients(BaseModel):
    signers: Optional[List[Dict[str, Any]]] = None


class EnvelopeCreateBody(BaseModel):
    emailSubject: Optional[str] = ""
    status: Optional[str] = "created"
    templateId: Optional[str] = None
    senderName: Optional[str] = None
    senderEmail: Optional[str] = None
    recipients: Optional[Dict[str, Any]] = None
    documents: Optional[List[Dict[str, Any]]] = None


@app.post("/restapi/v2.1/accounts/{accountId}/envelopes", status_code=201)
def create_envelope(accountId: str, body: EnvelopeCreateBody):
    return docusign_data.create_envelope(body.model_dump(exclude_none=True))


@app.get("/restapi/v2.1/accounts/{accountId}/envelopes/{envelopeId}")
def get_envelope(accountId: str, envelopeId: str):
    result = docusign_data.get_envelope(envelopeId)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class EnvelopeUpdateBody(BaseModel):
    status: str


@app.put("/restapi/v2.1/accounts/{accountId}/envelopes/{envelopeId}")
def update_envelope(accountId: str, envelopeId: str, body: EnvelopeUpdateBody):
    result = docusign_data.update_envelope(envelopeId, body.status)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/restapi/v2.1/accounts/{accountId}/envelopes/{envelopeId}/recipients")
def list_recipients(accountId: str, envelopeId: str):
    result = docusign_data.list_recipients(envelopeId)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/restapi/v2.1/accounts/{accountId}/envelopes/{envelopeId}/documents")
def list_documents(accountId: str, envelopeId: str):
    result = docusign_data.list_documents(envelopeId)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Templates ---

@app.get("/restapi/v2.1/accounts/{accountId}/templates")
def list_templates(accountId: str):
    return docusign_data.list_templates()
