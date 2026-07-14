"""FastAPI server wrapping kubernetes_data module as REST endpoints.

Mirrors a subset of the Kubernetes API surface (core/v1 + apps/v1).
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import kubernetes_data
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

app = FastAPI(title="Kubernetes API (Mock)", version="v1")
install_tracker(app)
install_admin_plane(app, store=kubernetes_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Namespaces ---

@app.get("/api/v1/namespaces")
def list_namespaces():
    return kubernetes_data.list_namespaces()


# --- Pods ---

@app.get("/api/v1/namespaces/{ns}/pods")
def list_pods(ns: str):
    result = kubernetes_data.list_pods(ns)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/api/v1/namespaces/{ns}/pods/{name}")
def get_pod(ns: str, name: str):
    result = kubernetes_data.get_pod(ns, name)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/api/v1/namespaces/{ns}/pods/{name}")
def delete_pod(ns: str, name: str):
    result = kubernetes_data.delete_pod(ns, name)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Deployments ---

@app.get("/apis/apps/v1/namespaces/{ns}/deployments")
def list_deployments(ns: str):
    result = kubernetes_data.list_deployments(ns)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/apis/apps/v1/namespaces/{ns}/deployments/{name}")
def get_deployment(ns: str, name: str):
    result = kubernetes_data.get_deployment(ns, name)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class ScaleSpec(BaseModel):
    replicas: int


class ScaleBody(BaseModel):
    spec: ScaleSpec


@app.patch("/apis/apps/v1/namespaces/{ns}/deployments/{name}/scale")
def scale_deployment(ns: str, name: str, body: ScaleBody):
    result = kubernetes_data.scale_deployment(ns, name, body.spec.replicas)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Services ---

@app.get("/api/v1/namespaces/{ns}/services")
def list_services(ns: str):
    result = kubernetes_data.list_services(ns)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Nodes ---

@app.get("/api/v1/nodes")
def list_nodes():
    return kubernetes_data.list_nodes()
