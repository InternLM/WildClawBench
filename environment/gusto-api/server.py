"""FastAPI server wrapping gusto_data module as REST endpoints.

Mirrors a subset of the Gusto v1 payroll API. Base path: /v1
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import gusto_data
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

app = FastAPI(title="Gusto Payroll API (Mock)", version="v1")
install_tracker(app)
install_admin_plane(app, store=gusto_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Company ---

@app.get("/v1/companies/{company_id}")
def get_company(company_id: str):
    result = gusto_data.get_company(company_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Employees ---

@app.get("/v1/companies/{company_id}/employees")
def list_company_employees(company_id: str):
    result = gusto_data.list_company_employees(company_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v1/employees/{employee_id}")
def get_employee(employee_id: str):
    result = gusto_data.get_employee(employee_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Payrolls ---

@app.get("/v1/companies/{company_id}/payrolls")
def list_company_payrolls(company_id: str, processed: Optional[bool] = None):
    result = gusto_data.list_company_payrolls(company_id, processed=processed)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v1/payrolls/{payroll_id}")
def get_payroll(payroll_id: str):
    result = gusto_data.get_payroll(payroll_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class PayrollCreate(BaseModel):
    pay_period_start: str
    pay_period_end: str
    check_date: Optional[str] = None


@app.post("/v1/companies/{company_id}/payrolls", status_code=201)
def create_payroll(company_id: str, body: PayrollCreate):
    result = gusto_data.create_payroll(
        company_id, pay_period_start=body.pay_period_start,
        pay_period_end=body.pay_period_end, check_date=body.check_date)
    if "error" in result:
        status = 404 if "not found" in result["error"] else 400
        return JSONResponse(status_code=status, content=result)
    return result


@app.put("/v1/payrolls/{payroll_id}/submit")
def submit_payroll(payroll_id: str):
    result = gusto_data.submit_payroll(payroll_id)
    if "error" in result:
        status = 404 if "not found" in result["error"] else 400
        return JSONResponse(status_code=status, content=result)
    return result


# --- Contractors ---

@app.get("/v1/companies/{company_id}/contractors")
def list_company_contractors(company_id: str):
    result = gusto_data.list_company_contractors(company_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
