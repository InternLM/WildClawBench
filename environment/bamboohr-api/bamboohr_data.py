"""Data access module for the BambooHR API mock service.

Mirrors a subset of the BambooHR v1 API (employees, time-off requests,
who's out). Records use stable string IDs. Mutations are held in process
memory and reset on container restart.
"""

import csv
import json
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_int, opt_str)

_store = get_store("bamboohr-api")
_API = "bamboohr-api"


def _store_insert(_table, _row):
    """Persist a newly-created row into the shared store (drift/injection-safe).

    Synthesizes the table's registered primary key from the row's ``id`` field
    when the row doesn't already carry it, so creates work regardless of whether
    the table was registered with primary_key="id" or a domain-specific key.
    """
    _t = _store.table(_table)
    if _t.primary_key not in _row and "id" in _row:
        _row = {**_row, _t.primary_key: _row["id"]}
    return _t.upsert(_row)

_store.register("employees", primary_key="id",
                initial_loader=lambda: _coerce_employees(_load("employees.json", "employees")))
_store.register("time_off", primary_key="id",
                initial_loader=lambda: _coerce_time_off(_load("time_off_requests.json", "time_off")))
_store.register("whos_out", primary_key="id",
                initial_loader=lambda: _coerce_whos_out(_load("whos_out.json", "whos_out")))
_store.register_document("company", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "company.json", encoding="utf-8")))


def _employees_rows():
    return _store.table("employees").rows()


def _time_off_rows():
    return _store.table("time_off").rows()


def _whos_out_rows():
    return _store.table("whos_out").rows()


def _company_doc():
    return _store.document("company").get()


VALID_TIME_OFF_STATUS = {"requested", "approved", "denied", "canceled"}


def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


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
        d = _strip_ctx(r)
        d["supervisorId"] = opt_str(r, "supervisorId", default="") or None
        out.append(d)
    return out


def _coerce_time_off(rows):
    out = []
    for r in rows:
        d = _strip_ctx(r)
        d["amount"] = opt_int(r, "amount", default=0)
        out.append(d)
    return out


def _coerce_whos_out(rows):
    return [_strip_ctx(r) for r in rows]






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
    employees = [{k: e.get(k) for k in fields} for e in _employees_rows()]
    return {"employees": employees}


def get_employee(employee_id):
    e = _find(_employees_rows(), employee_id)
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
    _store_insert("employees", emp)
    return emp


# ---------------------------------------------------------------------------
# Time-off requests
# ---------------------------------------------------------------------------

def list_time_off_requests(status=None, employee_id=None):
    results = list(_time_off_rows())
    if status:
        results = [r for r in results if r["status"] == status]
    if employee_id:
        results = [r for r in results if r["employeeId"] == employee_id]
    return results


def create_time_off_request(employeeId, type, start, end, amount=1,
                            unit="days", notes=None):
    if not _find(_employees_rows(), employeeId):
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
    _store_insert("time_off", req)
    return req


def update_time_off_status(request_id, status):
    req = _find(_time_off_rows(), request_id)
    if not req:
        return {"error": f"Time-off request {request_id} not found"}
    if status not in VALID_TIME_OFF_STATUS:
        return {"error": f"Invalid status: {status}"}
    req["status"] = status
    return req


def whos_out(start=None, end=None):
    results = list(_whos_out_rows())
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
        for e in _employees_rows():
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
    return _company_doc()

_store.eager_load()
