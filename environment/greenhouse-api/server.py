"""FastAPI server wrapping greenhouse_data module as REST endpoints.

Mirrors a subset of the Greenhouse Harvest API v1. Base path: /v1
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import greenhouse_data
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

app = FastAPI(title="Greenhouse Harvest API (Mock)", version="v1")
install_tracker(app)
install_admin_plane(app, store=greenhouse_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Candidates ---

@app.get("/v1/candidates")
def list_candidates():
    return greenhouse_data.list_candidates()


@app.get("/v1/candidates/{candidate_id}")
def get_candidate(candidate_id: str):
    result = greenhouse_data.get_candidate(candidate_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class CandidateCreate(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    source: Optional[str] = None


@app.post("/v1/candidates", status_code=201)
def create_candidate(body: CandidateCreate):
    result = greenhouse_data.create_candidate(**body.model_dump())
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Jobs ---

@app.get("/v1/jobs")
def list_jobs(status: Optional[str] = None):
    return greenhouse_data.list_jobs(status=status)


@app.get("/v1/jobs/{job_id}")
def get_job(job_id: str):
    result = greenhouse_data.get_job(job_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Applications ---

@app.get("/v1/applications")
def list_applications(job_id: Optional[str] = None, candidate_id: Optional[str] = None,
                      status: Optional[str] = None):
    return greenhouse_data.list_applications(job_id=job_id, candidate_id=candidate_id,
                                             status=status)


@app.get("/v1/applications/{application_id}")
def get_application(application_id: str):
    result = greenhouse_data.get_application(application_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/v1/applications/{application_id}/advance")
def advance_application(application_id: str):
    result = greenhouse_data.advance_application(application_id)
    if "error" in result:
        status = 404 if "not found" in result["error"] else 400
        return JSONResponse(status_code=status, content=result)
    return result


class RejectBody(BaseModel):
    reason: Optional[str] = None


@app.post("/v1/applications/{application_id}/reject")
def reject_application(application_id: str, body: Optional[RejectBody] = None):
    reason = body.reason if body else None
    result = greenhouse_data.reject_application(application_id, reason=reason)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Scorecards ---

@app.get("/v1/scorecards")
def list_scorecards(application_id: Optional[str] = None,
                    candidate_id: Optional[str] = None):
    return greenhouse_data.list_scorecards(application_id=application_id,
                                           candidate_id=candidate_id)
