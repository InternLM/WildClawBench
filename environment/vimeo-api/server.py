"""FastAPI server wrapping vimeo_data module as REST endpoints.

Mirrors a subset of the Vimeo API (api.vimeo.com): the authenticated user
(/me), videos, and other users. List endpoints return Vimeo's paged envelope
{"total", "page", "per_page", "data"}.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from typing import Optional

import vimeo_data
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

app = FastAPI(title="Vimeo API (Mock)", version="3.4")
install_tracker(app)
install_admin_plane(app, store=vimeo_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Authenticated user ---

@app.get("/me")
def get_me():
    return vimeo_data.get_me()


@app.get("/me/videos")
def get_my_videos(page: int = Query(default=1), per_page: int = Query(default=25)):
    return vimeo_data.get_my_videos(page=page, per_page=per_page)


# --- Videos ---

@app.get("/videos/{video_id}")
def get_video(video_id: str):
    result = vimeo_data.get_video(video_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Users ---

@app.get("/users/{user_id}")
def get_user(user_id: str):
    result = vimeo_data.get_user(user_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/users/{user_id}/videos")
def get_user_videos(
    user_id: str,
    page: int = Query(default=1),
    per_page: int = Query(default=25),
):
    result = vimeo_data.get_user_videos(user_id, page=page, per_page=per_page)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
