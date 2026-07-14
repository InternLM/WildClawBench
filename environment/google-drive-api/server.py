"""FastAPI server wrapping google_drive_data module as REST endpoints.

Mirrors Google Drive API v3 (subset).
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

import google_drive_data
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

app = FastAPI(title="Google Drive API (Mock)", version="v3")
install_tracker(app)
install_admin_plane(app, store=google_drive_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- About ---

@app.get("/drive/v3/about")
def get_about():
    return google_drive_data.get_about()


# --- Files ---

@app.get("/drive/v3/files")
def list_files(
    q: str = "",
    pageSize: int = Query(100, ge=1, le=1000),
    pageToken: Optional[str] = None,
    orderBy: str = "modifiedTime desc",
):
    return google_drive_data.list_files(q=q, page_size=pageSize, page_token=pageToken, order_by=orderBy)


@app.get("/drive/v3/files/{file_id}")
def get_file(file_id: str, alt: Optional[str] = None):
    if alt == "media":
        try:
            return google_drive_data.download_file_content(file_id)
        except google_drive_data.DownloadError as e:
            return JSONResponse(
                status_code=e.http_status,
                content={"error": {"code": e.http_status, "message": e.message,
                                   "status": e.code.upper()}},
            )
    result = google_drive_data.get_file(file_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class FileCreateBody(BaseModel):
    name: str
    mimeType: str
    parents: Optional[List[str]] = None
    size: Optional[int] = 0
    ownerEmail: Optional[str] = "amelia@orbit-labs.com"


@app.post("/drive/v3/files", status_code=201)
def create_file(body: FileCreateBody):
    parent = body.parents[0] if body.parents else None
    result = google_drive_data.create_file(
        name=body.name, mime_type=body.mimeType, parent_id=parent,
        owner_email=body.ownerEmail, size=body.size or 0,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class FileUpdateBody(BaseModel):
    name: Optional[str] = None
    addParents: Optional[str] = None
    starred: Optional[bool] = None
    trashed: Optional[bool] = None


@app.patch("/drive/v3/files/{file_id}")
def update_file(file_id: str, body: FileUpdateBody):
    result = google_drive_data.update_file(
        file_id,
        name=body.name,
        parent_id=body.addParents,
        starred=body.starred,
        trashed=body.trashed,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/drive/v3/files/{file_id}/trash")
def trash_file(file_id: str):
    result = google_drive_data.trash_file(file_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/drive/v3/files/{file_id}")
def delete_file(file_id: str):
    result = google_drive_data.delete_file(file_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Permissions ---

@app.get("/drive/v3/files/{file_id}/permissions")
def list_permissions(file_id: str):
    result = google_drive_data.list_permissions(file_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class PermissionCreateBody(BaseModel):
    type: str  # "user", "group", "domain", "anyone"
    role: str  # "owner", "writer", "commenter", "reader"
    emailAddress: Optional[str] = None
    displayName: Optional[str] = None


@app.post("/drive/v3/files/{file_id}/permissions", status_code=201)
def create_permission(file_id: str, body: PermissionCreateBody):
    result = google_drive_data.create_permission(
        file_id,
        type=body.type,
        role=body.role,
        email_address=body.emailAddress,
        display_name=body.displayName,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/drive/v3/files/{file_id}/permissions/{permission_id}")
def delete_permission(file_id: str, permission_id: str):
    result = google_drive_data.delete_permission(file_id, permission_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
