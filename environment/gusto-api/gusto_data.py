"""Data access module for the Gusto Payroll API mock service.

Mirrors a subset of the Gusto v1 API: company, employees, compensations,
payrolls, contractors. Records use stable string IDs. Mutations are held in
process memory and reset on container restart.
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
    read_seed_with_ctx, get_store,
    strict_bool,
    opt_int,
    opt_float,
)

_store = get_store("gusto-api")
_API = "gusto-api"


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
_store.register("compensations", primary_key="id",
                initial_loader=lambda: _coerce_compensations(_load("compensations.json", "compensations")))
_store.register("payrolls", primary_key="id",
                initial_loader=lambda: _coerce_payrolls(_load("payrolls.json", "payrolls")))
_store.register("contractors", primary_key="id",
                initial_loader=lambda: _coerce_contractors(_load("contractors.json", "contractors")))
_store.register_document("company", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "company.json", encoding="utf-8")))


def _employees_rows():
    return _store.table("employees").rows()


def _compensations_rows():
    return _store.table("compensations").rows()


def _payrolls_rows():
    return _store.table("payrolls").rows()


def _contractors_rows():
    return _store.table("contractors").rows()


def _company_doc():
    return _store.document("company").get()



_API = "gusto-api"


def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now_date():
    return datetime.utcnow().strftime("%Y-%m-%d")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _to_float(v, default=0.0):
    if v is None or str(v).strip() == "":
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


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
        d["rate"] = opt_float(r, "rate", default=0.0)
        d["terminated"] = strict_bool(r, "terminated")
        out.append(d)
    return out


def _coerce_compensations(rows):
    out = []
    for r in rows:
        d = _strip_ctx(r)
        d["rate"] = opt_float(r, "rate", default=0.0)
        out.append(d)
    return out


def _coerce_payrolls(rows):
    out = []
    for r in rows:
        d = _strip_ctx(r)
        d["processed"] = strict_bool(r, "processed")
        d["gross_pay"] = opt_float(r, "gross_pay", default=0.0)
        d["net_pay"] = opt_float(r, "net_pay", default=0.0)
        d["employee_count"] = opt_int(r, "employee_count", default=0)
        out.append(d)
    return out


def _coerce_contractors(rows):
    out = []
    for r in rows:
        d = _strip_ctx(r)
        d["hourly_rate"] = opt_float(r, "hourly_rate", default=0.0)
        out.append(d)
    return out


_company = None

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _find(store, obj_id):
    return next((x for x in store if x["id"] == obj_id), None)


def _comp_for(employee_id):
    return next((c for c in _compensations_rows() if c["employee_id"] == employee_id), None)


# ---------------------------------------------------------------------------
# Company
# ---------------------------------------------------------------------------

def get_company(company_id):
    if company_id != _company_doc()["id"]:
        return {"error": f"Company {company_id} not found"}
    return _company_doc()


# ---------------------------------------------------------------------------
# Employees / compensations
# ---------------------------------------------------------------------------

def list_company_employees(company_id):
    if company_id != _company_doc()["id"]:
        return {"error": f"Company {company_id} not found"}
    out = []
    for e in _employees_rows():
        if e["company_id"] != company_id:
            continue
        rec = dict(e)
        rec["compensation"] = _comp_for(e["id"])
        out.append(rec)
    return out


def get_employee(employee_id):
    e = _find(_employees_rows(), employee_id)
    if not e:
        return {"error": f"Employee {employee_id} not found"}
    rec = dict(e)
    rec["compensation"] = _comp_for(employee_id)
    return rec


# ---------------------------------------------------------------------------
# Payrolls
# ---------------------------------------------------------------------------

def list_company_payrolls(company_id, processed=None):
    if company_id != _company_doc()["id"]:
        return {"error": f"Company {company_id} not found"}
    results = [p for p in _payrolls_rows() if p["company_id"] == company_id]
    if processed is not None:
        results = [p for p in results if p["processed"] == processed]
    return results


def get_payroll(payroll_id):
    p = _find(_payrolls_rows(), payroll_id)
    if not p:
        return {"error": f"Payroll {payroll_id} not found"}
    return p


def create_payroll(company_id, pay_period_start, pay_period_end, check_date=None):
    if company_id != _company_doc()["id"]:
        return {"error": f"Company {company_id} not found"}
    if not pay_period_start or not pay_period_end:
        return {"error": "pay_period_start and pay_period_end are required"}
    p = {
        "id": _new_id("pay"),
        "company_id": company_id,
        "pay_period_start": pay_period_start,
        "pay_period_end": pay_period_end,
        "check_date": check_date or "",
        "processed": False,
        "gross_pay": 0.0,
        "net_pay": 0.0,
        "employee_count": len([e for e in _employees_rows()
                               if e["company_id"] == company_id and not e["terminated"]]),
    }
    _store_insert("payrolls", p)
    return p


def submit_payroll(payroll_id):
    p = _find(_payrolls_rows(), payroll_id)
    if not p:
        return {"error": f"Payroll {payroll_id} not found"}
    if p["processed"]:
        return {"error": f"Payroll {payroll_id} already processed"}
    # Compute gross from semimonthly slice of annual / hourly comp.
    gross = 0.0
    for e in _employees_rows():
        if e["company_id"] != p["company_id"] or e["terminated"]:
            continue
        comp = _comp_for(e["id"]) or {}
        rate = comp.get("rate", e.get("rate", 0.0))
        unit = comp.get("payment_unit", e.get("payment_unit", "Year"))
        if unit == "Year":
            gross += rate / 24.0  # 24 semimonthly periods
        elif unit == "Hour":
            gross += rate * 86.67  # ~ semimonthly hours
        else:
            gross += rate
    gross = round(gross, 2)
    p["processed"] = True
    p["gross_pay"] = gross
    p["net_pay"] = round(gross * 0.726, 2)
    return p


# ---------------------------------------------------------------------------
# Contractors
# ---------------------------------------------------------------------------

def list_company_contractors(company_id):
    if company_id != _company_doc()["id"]:
        return {"error": f"Company {company_id} not found"}
    return [c for c in _contractors_rows() if c["company_id"] == company_id]

_store.eager_load()
