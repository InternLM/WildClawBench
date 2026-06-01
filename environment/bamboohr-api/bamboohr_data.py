"""Data access module for the BambooHR API mock service.

Mirrors a subset of the BambooHR v1 API (employees, time-off requests,
who's out). Records use stable string IDs. Mutations are held in process
memory and reset on container restart.
"""

import csv
import json
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

VALID_TIME_OFF_STATUS = {"requested", "approved", "denied", "canceled"}


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now_date():
    return datetime.utcnow().strftime("%Y-%m-%d")


def _to_int(v, default=0):
    if v is None or str(v).strip() == "":
        return default
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_employees(rows):
    out = []
    for r in rows:
        d = dict(r)
        d["supervisorId"] = r["supervisorId"] or None
        out.append(d)
    return out


def _coerce_time_off(rows):
    out = []
    for r in rows:
        d = dict(r)
        d["amount"] = _to_int(r["amount"])
        out.append(d)
    return out


def _coerce_whos_out(rows):
    return [dict(r) for r in rows]


_employees = _coerce_employees(_load("employees.csv"))
_time_off = _coerce_time_off(_load("time_off_requests.csv"))
_whos_out = _coerce_whos_out(_load("whos_out.csv"))

with open(DATA_DIR / "company.json", encoding="utf-8") as _f:
    _company = json.load(_f)

_employees_store = deepcopy(_employees)
_time_off_store = deepcopy(_time_off)
_whos_out_store = deepcopy(_whos_out)
_company_store = deepcopy(_company)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _find(store, obj_id):
    return next((x for x in store if x["id"] == obj_id), None)


# ---------------------------------------------------------------------------
# Employees
# ---------------------------------------------------------------------------

def employees_directory():
    fields = ["id", "firstName", "lastName", "workEmail", "department",
              "jobTitle", "location", "hireDate", "status", "supervisorId"]
    employees = [{k: e.get(k) for k in fields} for e in _employees_store]
    return {"employees": employees}


def get_employee(employee_id):
    e = _find(_employees_store, employee_id)
    if not e:
        return {"error": f"Employee {employee_id} not found"}
    return e


def create_employee(firstName, lastName, workEmail=None, department=None,
                    jobTitle=None, location=None, hireDate=None, supervisorId=None):
    if not firstName or not lastName:
        return {"error": "firstName and lastName are required"}
    emp = {
        "id": _new_id("emp"),
        "firstName": firstName,
        "lastName": lastName,
        "workEmail": workEmail or "",
        "department": department or "",
        "jobTitle": jobTitle or "",
        "location": location or "",
        "hireDate": hireDate or _now_date(),
        "status": "Active",
        "supervisorId": supervisorId or None,
    }
    _employees_store.append(emp)
    return emp


# ---------------------------------------------------------------------------
# Time-off requests
# ---------------------------------------------------------------------------

def list_time_off_requests(status=None, employee_id=None):
    results = list(_time_off_store)
    if status:
        results = [r for r in results if r["status"] == status]
    if employee_id:
        results = [r for r in results if r["employeeId"] == employee_id]
    return results


def create_time_off_request(employeeId, type, start, end, amount=1,
                            unit="days", notes=None):
    if not _find(_employees_store, employeeId):
        return {"error": f"Employee {employeeId} not found"}
    req = {
        "id": _new_id("tor"),
        "employeeId": employeeId,
        "type": type or "Vacation",
        "status": "requested",
        "start": start,
        "end": end,
        "amount": _to_int(amount, 1),
        "unit": unit or "days",
        "notes": notes or "",
        "created": _now_date(),
    }
    _time_off_store.append(req)
    return req


def update_time_off_status(request_id, status):
    req = _find(_time_off_store, request_id)
    if not req:
        return {"error": f"Time-off request {request_id} not found"}
    if status not in VALID_TIME_OFF_STATUS:
        return {"error": f"Invalid status: {status}"}
    req["status"] = status
    return req


def whos_out(start=None, end=None):
    results = list(_whos_out_store)
    if start:
        results = [r for r in results if r["end"] >= start]
    if end:
        results = [r for r in results if r["start"] <= end]
    return results


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

def get_report(report_id):
    """Synthesize a simple report. report_id 1 = headcount by department."""
    if str(report_id) == "1":
        by_dept = {}
        for e in _employees_store:
            if e.get("status") == "Active":
                by_dept[e["department"]] = by_dept.get(e["department"], 0) + 1
        rows = [{"department": d, "headcount": c} for d, c in sorted(by_dept.items())]
        return {
            "title": "Headcount by Department",
            "fields": [{"id": "department", "name": "Department"},
                       {"id": "headcount", "name": "Headcount"}],
            "employees": rows,
        }
    return {"error": f"Report {report_id} not found"}


def get_company():
    return _company_store
