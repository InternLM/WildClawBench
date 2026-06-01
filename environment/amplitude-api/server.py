"""FastAPI server wrapping amplitude_data module as REST endpoints.

Mirrors a subset of Amplitude: the HTTP V2 event-upload API, the event
segmentation chart API, and the user-activity stream.
"""

from fastapi import FastAPI, Query, Body
from fastapi.responses import JSONResponse
from typing import Optional

import amplitude_data
try:
    from tracking_middleware import install_tracker
except ModuleNotFoundError:  # standalone run without the shared module on sys.path
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

app = FastAPI(title="Amplitude API (Mock)", version="2")
install_tracker(app)


@app.get("/health")
def health():
    return {"status": "ok"}


# --- HTTP V2 event upload ---

@app.post("/2/httpapi")
def httpapi(body: dict = Body(...)):
    return amplitude_data.ingest(body)


# --- Event segmentation ---

@app.get("/api/2/events/segmentation")
def segmentation(
    e: Optional[str] = Query(None),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
):
    return amplitude_data.segmentation(event=e, start=start, end=end)


# --- User activity ---

@app.get("/api/2/useractivity")
def user_activity(user: str = Query(...)):
    result = amplitude_data.user_activity(user)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
