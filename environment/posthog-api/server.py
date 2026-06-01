"""FastAPI server wrapping posthog_data module as REST endpoints.

Mirrors a subset of PostHog: the capture endpoint, project events / persons /
feature flags read APIs, and the /decide flag-evaluation endpoint.
"""

from fastapi import FastAPI, Query, Body
from fastapi.responses import JSONResponse
from typing import Optional

import posthog_data
try:
    from tracking_middleware import install_tracker
except ModuleNotFoundError:  # standalone run without the shared module on sys.path
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

app = FastAPI(title="PostHog API (Mock)", version="1")
install_tracker(app)


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Capture (write) ---

@app.post("/capture")
def capture(body: dict = Body(...)):
    return posthog_data.capture(body)


# --- Decide (flag evaluation) ---

@app.post("/decide")
def decide(body: dict = Body(...)):
    return posthog_data.decide(body)


# --- Project reads ---

@app.get("/api/projects/{project_id}/events")
def list_events(
    project_id: int,
    event: Optional[str] = Query(None),
    distinct_id: Optional[str] = Query(None),
):
    return posthog_data.list_events(project_id, event=event, distinct_id=distinct_id)


@app.get("/api/projects/{project_id}/feature_flags")
def list_feature_flags(project_id: int):
    return posthog_data.list_feature_flags(project_id)


@app.get("/api/projects/{project_id}/persons")
def list_persons(project_id: int):
    return posthog_data.list_persons(project_id)
