"""FastAPI server wrapping okta_data module as REST endpoints.

Mirrors a subset of the Okta Management API. Base path: /api/v1
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import okta_data
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

app = FastAPI(title="Okta API (Mock)", version="v1")
install_tracker(app)
install_admin_plane(app, store=okta_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Users ---

@app.get("/api/v1/users")
def list_users(status: Optional[str] = None, q: Optional[str] = None):
    return okta_data.list_users(status=status, q=q)


@app.get("/api/v1/users/{user_id}")
def get_user(user_id: str):
    result = okta_data.get_user(user_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class UserProfile(BaseModel):
    firstName: str
    lastName: str
    email: str
    login: Optional[str] = None


class UserCreateBody(BaseModel):
    profile: UserProfile


@app.post("/api/v1/users", status_code=201)
def create_user(body: UserCreateBody, activate: bool = True):
    return okta_data.create_user(
        first_name=body.profile.firstName,
        last_name=body.profile.lastName,
        email=body.profile.email,
        login=body.profile.login,
        activate=activate,
    )


@app.post("/api/v1/users/{user_id}/lifecycle/activate")
def activate_user(user_id: str):
    result = okta_data.activate_user(user_id)
    if "error" in result:
        status = 404 if "not found" in result["error"] else 403
        return JSONResponse(status_code=status, content=result)
    return result


@app.post("/api/v1/users/{user_id}/lifecycle/suspend")
def suspend_user(user_id: str):
    result = okta_data.suspend_user(user_id)
    if "error" in result:
        status = 404 if "not found" in result["error"] else 403
        return JSONResponse(status_code=status, content=result)
    return result


@app.post("/api/v1/users/{user_id}/lifecycle/deactivate")
def deactivate_user(user_id: str):
    result = okta_data.deactivate_user(user_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Groups ---

@app.get("/api/v1/groups")
def list_groups(q: Optional[str] = None):
    return okta_data.list_groups(q=q)


@app.get("/api/v1/groups/{group_id}")
def get_group(group_id: str):
    result = okta_data.get_group(group_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/api/v1/groups/{group_id}/users")
def list_group_users(group_id: str):
    result = okta_data.list_group_users(group_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Apps ---

@app.get("/api/v1/apps")
def list_apps(status: Optional[str] = None):
    return okta_data.list_apps(status=status)
