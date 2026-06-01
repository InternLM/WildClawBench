"""FastAPI server wrapping klaviyo_data as REST endpoints.

Mirrors a subset of the Klaviyo API (JSON:API style): profiles, lists, and
campaigns. Responses use the JSON:API envelope, e.g.
{"data": [{"type": "profile", "id": ..., "attributes": {...}}]}.
"""

from fastapi import FastAPI, Body, Query
from fastapi.responses import JSONResponse
from typing import Optional

import klaviyo_data
try:
    from tracking_middleware import install_tracker
except ModuleNotFoundError:  # standalone run without the shared module on sys.path
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

app = FastAPI(title="Klaviyo API (Mock)", version="2024-10-15")
install_tracker(app)


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Profiles ---

@app.get("/api/profiles")
def list_profiles(email: Optional[str] = None):
    return klaviyo_data.list_profiles(email=email)


@app.get("/api/profiles/{profile_id}")
def get_profile(profile_id: str):
    result = klaviyo_data.get_profile(profile_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/api/profiles", status_code=201)
def create_profile(body: dict = Body(...)):
    data = body.get("data") or {}
    attrs = data.get("attributes") or {}
    email = attrs.get("email")
    if not email:
        return JSONResponse(
            status_code=400,
            content={"error": "invalid request", "message": "data.attributes.email is required"},
        )
    location = attrs.get("location") or {}
    result = klaviyo_data.create_profile(
        email=email,
        first_name=attrs.get("first_name", ""),
        last_name=attrs.get("last_name", ""),
        phone_number=attrs.get("phone_number", ""),
        organization=attrs.get("organization", ""),
        title=attrs.get("title", ""),
        city=location.get("city", ""),
        region=location.get("region", ""),
        country=location.get("country", ""),
    )
    if isinstance(result, dict) and "error" in result:
        status = 409 if result.get("error") == "duplicate profile" else 400
        return JSONResponse(status_code=status, content=result)
    return result


# --- Lists ---

@app.get("/api/lists")
def list_lists():
    return klaviyo_data.list_lists()


# --- Campaigns ---

@app.get("/api/campaigns")
def list_campaigns(
    status: Optional[str] = None,
    channel: Optional[str] = None,
):
    return klaviyo_data.list_campaigns(status=status, channel=channel)
