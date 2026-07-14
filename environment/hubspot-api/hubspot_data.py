"""Data access module for the HubSpot CRM API mock service.

Mirrors a subset of the HubSpot CRM v3 API. Objects are returned in the
HubSpot shape: {"id": ..., "properties": {...}, "createdAt": ..., "updatedAt": ...}.
Mutations (created/updated contacts and deals) reset on container restart.
"""

import csv
from copy import deepcopy
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store,
    strict_int,
    strict_bool,
    opt_float,
)

_store = get_store("hubspot-api")
_API = "hubspot-api"

_store.register("pipelines", primary_key="id",
                initial_loader=lambda: _coerce_stages(_load("pipeline_stages.json", "pipelines")))


def _pipelines_rows():
    return _store.table("pipelines").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _to_float(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


# Property keys that make up each object's "properties" map.
_CONTACT_PROPS = ["firstname", "lastname", "email", "phone", "jobtitle",
                  "company", "lifecyclestage", "createdate", "lastmodifieddate"]
_COMPANY_PROPS = ["name", "domain", "industry", "city", "state",
                  "numberofemployees", "annualrevenue", "createdate"]
_DEAL_PROPS = ["dealname", "pipeline", "dealstage", "amount", "closedate",
               "dealtype", "createdate", "lastmodifieddate"]


# ---------------------------------------------------------------------------
# Load + coerce into HubSpot object shape
# ---------------------------------------------------------------------------

def _coerce_objects(rows, prop_keys, extra=None):
    out = []
    for r in rows:
        props = {k: r.get(k, "") for k in prop_keys}
        obj = {
            "id": r["id"],
            "properties": props,
            "createdAt": r.get("createdate") or _now(),
            "updatedAt": r.get("lastmodifieddate") or r.get("createdate") or _now(),
            "archived": False,
        }
        if extra:
            extra(r, obj)
        out.append(obj)
    return out


def _deal_extra(r, obj):
    # Keep association ids on the object (outside `properties`) for filtering.
    obj["_company"] = r.get("associated_company") or None
    obj["_contact"] = r.get("associated_contact") or None


def _coerce_stages(rows):
    pipelines = {}
    for r in rows:
        pid = r["pipeline_id"]
        pipelines.setdefault(pid, {
            "id": pid,
            "label": r["pipeline_label"],
            "displayOrder": 0,
            "stages": [],
        })
        pipelines[pid]["stages"].append({
            "id": r["stage_id"],
            "label": r["stage_label"],
            "displayOrder": strict_int(r, "display_order"),
            "metadata": {"isClosed": str(strict_bool(r, "closed")).lower(),
                         "probability": str(opt_float(r, "probability", default=0.0))},
        })
    return list(pipelines.values())


_contacts = _coerce_objects(_load("contacts.json", "contacts"), _CONTACT_PROPS)
_companies = _coerce_objects(_load("companies.json", "companies"), _COMPANY_PROPS)
_deals = _coerce_objects(_load("deals.json", "deals"), _DEAL_PROPS, extra=_deal_extra)





# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_id():
    return str(uuid.uuid4().int % 10**12)


def _public(obj):
    return {k: v for k, v in obj.items() if not k.startswith("_")}


def _paginate(items, limit, after):
    try:
        offset = int(after) if after else 0
    except (TypeError, ValueError):
        offset = 0
    limit = max(1, min(int(limit), 100))
    page = items[offset: offset + limit]
    body = {"results": [_public(o) for o in page]}
    if offset + limit < len(items):
        body["paging"] = {"next": {"after": str(offset + limit)}}
    return body


def _find(store, obj_id):
    return next((o for o in store if o["id"] == str(obj_id)), None)


# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------

def list_contacts(limit=10, after=None):
    return _paginate(_contacts, limit, after)


def get_contact(contact_id):
    c = _find(_contacts, contact_id)
    if not c:
        return {"error": f"Contact {contact_id} not found", "category": "OBJECT_NOT_FOUND"}
    return _public(c)


def create_contact(properties):
    now = _now()
    props = {k: "" for k in _CONTACT_PROPS}
    props.update({k: v for k, v in (properties or {}).items()})
    props["createdate"] = now
    props["lastmodifieddate"] = now
    contact = {
        "id": _new_id(),
        "properties": props,
        "createdAt": now,
        "updatedAt": now,
        "archived": False,
    }
    _contacts.append(contact)
    return _public(contact)


def update_contact(contact_id, properties):
    c = _find(_contacts, contact_id)
    if not c:
        return {"error": f"Contact {contact_id} not found", "category": "OBJECT_NOT_FOUND"}
    c["properties"].update({k: v for k, v in (properties or {}).items()})
    c["properties"]["lastmodifieddate"] = _now()
    c["updatedAt"] = _now()
    return _public(c)


# ---------------------------------------------------------------------------
# Companies
# ---------------------------------------------------------------------------

def list_companies(limit=10, after=None):
    return _paginate(_companies, limit, after)


def get_company(company_id):
    c = _find(_companies, company_id)
    if not c:
        return {"error": f"Company {company_id} not found", "category": "OBJECT_NOT_FOUND"}
    return _public(c)


# ---------------------------------------------------------------------------
# Deals
# ---------------------------------------------------------------------------

def list_deals(limit=10, after=None):
    return _paginate(_deals, limit, after)


def get_deal(deal_id):
    d = _find(_deals, deal_id)
    if not d:
        return {"error": f"Deal {deal_id} not found", "category": "OBJECT_NOT_FOUND"}
    return _public(d)


def _valid_stage(pipeline_id, stage_id):
    pipe = next((p for p in _pipelines_rows() if p["id"] == pipeline_id), None)
    if not pipe:
        return False
    return any(s["id"] == stage_id for s in pipe["stages"])


def create_deal(properties):
    now = _now()
    props = {k: "" for k in _DEAL_PROPS}
    props.update({k: v for k, v in (properties or {}).items()})
    props.setdefault("pipeline", "default")
    if not props.get("dealstage"):
        props["dealstage"] = "appointmentscheduled"
    props["createdate"] = now
    props["lastmodifieddate"] = now
    deal = {
        "id": _new_id(),
        "properties": props,
        "createdAt": now,
        "updatedAt": now,
        "archived": False,
        "_company": None,
        "_contact": None,
    }
    _deals.append(deal)
    return _public(deal)


def update_deal(deal_id, properties):
    d = _find(_deals, deal_id)
    if not d:
        return {"error": f"Deal {deal_id} not found", "category": "OBJECT_NOT_FOUND"}
    props = properties or {}
    if "dealstage" in props:
        pipeline_id = props.get("pipeline", d["properties"].get("pipeline", "default"))
        if not _valid_stage(pipeline_id, props["dealstage"]):
            return {"error": f"Invalid stage {props['dealstage']} for pipeline {pipeline_id}",
                    "category": "VALIDATION_ERROR"}
    d["properties"].update(props)
    d["properties"]["lastmodifieddate"] = _now()
    d["updatedAt"] = _now()
    return _public(d)


# ---------------------------------------------------------------------------
# Pipelines
# ---------------------------------------------------------------------------

def list_deal_pipelines():
    return {"results": deepcopy(_pipelines_rows())}

_store.eager_load()
