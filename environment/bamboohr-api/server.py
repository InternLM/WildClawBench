"""FastAPI server wrapping bamboohr_data module as REST endpoints.

Mirrors a subset of the BambooHR v1 API. Base path: /api/gateway.php/{company}/v1
The {company} path segment is accepted but not validated against seed data.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import bamboohr_data
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

app = FastAPI(title="BambooHR API (Mock)", version="v1")
install_tracker(app)
install_admin_plane(app, store=bamboohr_data._store)
_BASE = "/api/gateway.php/{company}/v1"


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Company ---

@app.get(_BASE + "/company")
def get_company(company: str):
    return bamboohr_data.get_company()


# --- Employees ---

@app.get(_BASE + "/employees/directory")
def employees_directory(company: str):
    return bamboohr_data.employees_directory()


@app.get(_BASE + "/employees/{employee_id}")
def get_employee(company: str, employee_id: str):
    result = bamboohr_data.get_employee(employee_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class EmployeeCreate(BaseModel):
    firstName: str
    lastName: str
    workEmail: Optional[str] = None
    department: Optional[str] = None
    jobTitle: Optional[str] = None
    location: Optional[str] = None
    hireDate: Optional[str] = None
    supervisorId: Optional[str] = None


@app.post(_BASE + "/employees", status_code=201)
def create_employee(company: str, body: EmployeeCreate):
    result = bamboohr_data.create_employee(**body.model_dump())
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Time-off ---

@app.get(_BASE + "/time_off/requests")
def list_time_off_requests(company: str, status: Optional[str] = None,
                           employeeId: Optional[str] = None):
    return bamboohr_data.list_time_off_requests(status=status, employee_id=employeeId)


class TimeOffCreate(BaseModel):
    employeeId: str
    type: Optional[str] = "Vacation"
    start: str
    end: str
    amount: Optional[int] = 1
    unit: Optional[str] = "days"
    notes: Optional[str] = None


@app.post(_BASE + "/time_off/requests", status_code=201)
def create_time_off_request(company: str, body: TimeOffCreate):
    result = bamboohr_data.create_time_off_request(
        employeeId=body.employeeId, type=body.type, start=body.start, end=body.end,
        amount=body.amount, unit=body.unit, notes=body.notes)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class TimeOffStatus(BaseModel):
    status: str


@app.put(_BASE + "/time_off/requests/{request_id}/status")
def update_time_off_status(company: str, request_id: str, body: TimeOffStatus):
    result = bamboohr_data.update_time_off_status(request_id, body.status)
    if "error" in result:
        status = 404 if "not found" in result["error"] else 400
        return JSONResponse(status_code=status, content=result)
    return result


@app.get(_BASE + "/time_off/whos_out")
def whos_out(company: str, start: Optional[str] = None, end: Optional[str] = None):
    return bamboohr_data.whos_out(start=start, end=end)


# --- Reports ---

@app.get(_BASE + "/reports/{report_id}")
def get_report(company: str, report_id: str):
    result = bamboohr_data.get_report(report_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
