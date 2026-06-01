"""Data access module for the Greenhouse Harvest API mock service.

Mirrors a subset of the Greenhouse v1 (Harvest) API: candidates, jobs,
applications, scorecards. Records use stable string IDs. Mutations are held
in process memory and reset on container restart.
"""

import csv
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

# Ordered hiring pipeline stages used to advance applications.
STAGES = ["Application Review", "Interview", "Offer", "Hired"]


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


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

def _coerce_candidates(rows):
    return [dict(r) for r in rows]


def _coerce_jobs(rows):
    out = []
    for r in rows:
        d = dict(r)
        d["closed_at"] = r["closed_at"] or None
        out.append(d)
    return out


def _coerce_applications(rows):
    return [dict(r) for r in rows]


def _coerce_scorecards(rows):
    out = []
    for r in rows:
        d = dict(r)
        d["rating"] = _to_int(r["rating"])
        out.append(d)
    return out


_candidates = _coerce_candidates(_load("candidates.csv"))
_jobs = _coerce_jobs(_load("jobs.csv"))
_applications = _coerce_applications(_load("applications.csv"))
_scorecards = _coerce_scorecards(_load("scorecards.csv"))

_candidates_store = deepcopy(_candidates)
_jobs_store = deepcopy(_jobs)
_applications_store = deepcopy(_applications)
_scorecards_store = deepcopy(_scorecards)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _find(store, obj_id):
    return next((x for x in store if x["id"] == obj_id), None)


# ---------------------------------------------------------------------------
# Candidates
# ---------------------------------------------------------------------------

def list_candidates():
    return list(_candidates_store)


def get_candidate(candidate_id):
    c = _find(_candidates_store, candidate_id)
    if not c:
        return {"error": f"Candidate {candidate_id} not found"}
    return c


def create_candidate(first_name, last_name, email=None, phone=None,
                     company=None, title=None, source=None):
    if not first_name or not last_name:
        return {"error": "first_name and last_name are required"}
    c = {
        "id": _new_id("cand"),
        "first_name": first_name,
        "last_name": last_name,
        "email": email or "",
        "phone": phone or "",
        "company": company or "",
        "title": title or "",
        "source": source or "API",
        "created_at": _now(),
    }
    _candidates_store.append(c)
    return c


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

def list_jobs(status=None):
    results = list(_jobs_store)
    if status:
        results = [j for j in results if j["status"] == status]
    return results


def get_job(job_id):
    j = _find(_jobs_store, job_id)
    if not j:
        return {"error": f"Job {job_id} not found"}
    return j


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

def list_applications(job_id=None, candidate_id=None, status=None):
    results = list(_applications_store)
    if job_id:
        results = [a for a in results if a["job_id"] == job_id]
    if candidate_id:
        results = [a for a in results if a["candidate_id"] == candidate_id]
    if status:
        results = [a for a in results if a["status"] == status]
    return results


def get_application(application_id):
    a = _find(_applications_store, application_id)
    if not a:
        return {"error": f"Application {application_id} not found"}
    return a


def advance_application(application_id):
    a = _find(_applications_store, application_id)
    if not a:
        return {"error": f"Application {application_id} not found"}
    if a["status"] != "active":
        return {"error": f"Application {application_id} is not active"}
    current = a.get("current_stage")
    try:
        idx = STAGES.index(current)
    except ValueError:
        idx = 0
    if idx >= len(STAGES) - 1:
        a["current_stage"] = "Hired"
        a["status"] = "hired"
    else:
        a["current_stage"] = STAGES[idx + 1]
        if a["current_stage"] == "Hired":
            a["status"] = "hired"
    a["last_activity_at"] = _now()
    return a


def reject_application(application_id, reason=None):
    a = _find(_applications_store, application_id)
    if not a:
        return {"error": f"Application {application_id} not found"}
    a["status"] = "rejected"
    a["rejection_reason"] = reason or "Not a fit"
    a["last_activity_at"] = _now()
    return a


# ---------------------------------------------------------------------------
# Scorecards
# ---------------------------------------------------------------------------

def list_scorecards(application_id=None, candidate_id=None):
    results = list(_scorecards_store)
    if application_id:
        results = [s for s in results if s["application_id"] == application_id]
    if candidate_id:
        results = [s for s in results if s["candidate_id"] == candidate_id]
    return results
