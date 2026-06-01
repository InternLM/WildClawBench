"""Data access module for the Gusto Payroll API mock service.

Mirrors a subset of the Gusto v1 API: company, employees, compensations,
payrolls, contractors. Records use stable string IDs. Mutations are held in
process memory and reset on container restart.
"""

import csv
import json
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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
        d = dict(r)
        d["rate"] = _to_float(r["rate"])
        d["terminated"] = _to_bool(r["terminated"])
        out.append(d)
    return out


def _coerce_compensations(rows):
    out = []
    for r in rows:
        d = dict(r)
        d["rate"] = _to_float(r["rate"])
        out.append(d)
    return out


def _coerce_payrolls(rows):
    out = []
    for r in rows:
        d = dict(r)
        d["processed"] = _to_bool(r["processed"])
        d["gross_pay"] = _to_float(r["gross_pay"])
        d["net_pay"] = _to_float(r["net_pay"])
        d["employee_count"] = _to_int(r["employee_count"])
        out.append(d)
    return out


def _coerce_contractors(rows):
    out = []
    for r in rows:
        d = dict(r)
        d["hourly_rate"] = _to_float(r["hourly_rate"])
        out.append(d)
    return out


_company = None
with open(DATA_DIR / "company.json", encoding="utf-8") as _f:
    _company = json.load(_f)

_employees = _coerce_employees(_load("employees.csv"))
_compensations = _coerce_compensations(_load("compensations.csv"))
_payrolls = _coerce_payrolls(_load("payrolls.csv"))
_contractors = _coerce_contractors(_load("contractors.csv"))

_company_store = deepcopy(_company)
_employees_store = deepcopy(_employees)
_compensations_store = deepcopy(_compensations)
_payrolls_store = deepcopy(_payrolls)
_contractors_store = deepcopy(_contractors)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _find(store, obj_id):
    return next((x for x in store if x["id"] == obj_id), None)


def _comp_for(employee_id):
    return next((c for c in _compensations_store if c["employee_id"] == employee_id), None)


# ---------------------------------------------------------------------------
# Company
# ---------------------------------------------------------------------------

def get_company(company_id):
    if company_id != _company_store["id"]:
        return {"error": f"Company {company_id} not found"}
    return _company_store


# ---------------------------------------------------------------------------
# Employees / compensations
# ---------------------------------------------------------------------------

def list_company_employees(company_id):
    if company_id != _company_store["id"]:
        return {"error": f"Company {company_id} not found"}
    out = []
    for e in _employees_store:
        if e["company_id"] != company_id:
            continue
        rec = dict(e)
        rec["compensation"] = _comp_for(e["id"])
        out.append(rec)
    return out


def get_employee(employee_id):
    e = _find(_employees_store, employee_id)
    if not e:
        return {"error": f"Employee {employee_id} not found"}
    rec = dict(e)
    rec["compensation"] = _comp_for(employee_id)
    return rec


# ---------------------------------------------------------------------------
# Payrolls
# ---------------------------------------------------------------------------

def list_company_payrolls(company_id, processed=None):
    if company_id != _company_store["id"]:
        return {"error": f"Company {company_id} not found"}
    results = [p for p in _payrolls_store if p["company_id"] == company_id]
    if processed is not None:
        results = [p for p in results if p["processed"] == processed]
    return results


def get_payroll(payroll_id):
    p = _find(_payrolls_store, payroll_id)
    if not p:
        return {"error": f"Payroll {payroll_id} not found"}
    return p


def create_payroll(company_id, pay_period_start, pay_period_end, check_date=None):
    if company_id != _company_store["id"]:
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
        "employee_count": len([e for e in _employees_store
                               if e["company_id"] == company_id and not e["terminated"]]),
    }
    _payrolls_store.append(p)
    return p


def submit_payroll(payroll_id):
    p = _find(_payrolls_store, payroll_id)
    if not p:
        return {"error": f"Payroll {payroll_id} not found"}
    if p["processed"]:
        return {"error": f"Payroll {payroll_id} already processed"}
    # Compute gross from semimonthly slice of annual / hourly comp.
    gross = 0.0
    for e in _employees_store:
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
    if company_id != _company_store["id"]:
        return {"error": f"Company {company_id} not found"}
    return [c for c in _contractors_store if c["company_id"] == company_id]
