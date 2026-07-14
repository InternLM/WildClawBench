"""FastAPI server wrapping linkedin_data module as REST endpoints.

Implements a subset of the LinkedIn API v2 surface. Base path: /v2
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import linkedin_data
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

app = FastAPI(title="LinkedIn API v2 (Mock)", version="2.0.0")
install_tracker(app)
install_admin_plane(app, store=linkedin_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Profile / connections ---

@app.get("/v2/me")
def get_me():
    return linkedin_data.get_me()


@app.get("/v2/connections")
def list_connections(start: int = Query(0, ge=0), count: int = Query(50, ge=1, le=100)):
    return linkedin_data.list_connections(start=start, count=count)


# --- Posts ---

@app.get("/v2/posts")
def list_posts(author_id: Optional[str] = None, start: int = Query(0, ge=0),
               count: int = Query(50, ge=1, le=100)):
    return linkedin_data.list_posts(author_id=author_id, start=start, count=count)


class PostCreateBody(BaseModel):
    commentary: str
    author_id: Optional[str] = None
    visibility: str = "PUBLIC"


@app.post("/v2/posts", status_code=201)
def create_post(body: PostCreateBody):
    return linkedin_data.create_post(
        commentary=body.commentary,
        author_id=body.author_id,
        visibility=body.visibility,
    )


@app.get("/v2/posts/{post_id}")
def get_post(post_id: str):
    result = linkedin_data.get_post(post_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Organizations ---

@app.get("/v2/organizations/{org_id}")
def get_organization(org_id: str):
    result = linkedin_data.get_organization(org_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Jobs ---

@app.get("/v2/jobs")
def search_jobs(keywords: Optional[str] = None, location: Optional[str] = None,
                start: int = Query(0, ge=0), count: int = Query(50, ge=1, le=100)):
    return linkedin_data.search_jobs(keywords=keywords, location=location, start=start, count=count)


@app.get("/v2/jobs/{job_id}")
def get_job(job_id: str):
    result = linkedin_data.get_job(job_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
