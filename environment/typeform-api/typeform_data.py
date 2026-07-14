"""Data access module for the Typeform API mock service."""

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
)

_store = get_store("typeform-api")
_API = "typeform-api"



def _store_patch(_table, _row_or_pk, _updates):
    """Persist field updates to a stored row (was: in-place mutation of a copy)."""
    _t = _store.table(_table)
    _pk = _row_or_pk.get(_t.primary_key, _row_or_pk.get("id")) if isinstance(_row_or_pk, dict) else _row_or_pk
    return _t.patch(_pk, _updates)


def _store_delete(_table, _row_or_pk):
    """Persist a row deletion (was: pop/remove on a copy)."""
    _t = _store.table(_table)
    _pk = _row_or_pk.get(_t.primary_key, _row_or_pk.get("id")) if isinstance(_row_or_pk, dict) else _row_or_pk
    return _t.delete(_pk)

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

_store.register("forms", primary_key="form_id",
                initial_loader=lambda: _coerce_forms(_load("forms.json", "forms")))
_store.register("fields", primary_key="field_id",
                initial_loader=lambda: _coerce_fields(_load("fields.json", "fields")))
_store.register("responses", primary_key="response_id",
                initial_loader=lambda: _coerce_responses(_load("responses.json", "responses")))
_store.register("answers", primary_key="_pk",
                initial_loader=lambda: [{**r, "_pk": f"{r['response_id']}@{r['field_id']}"}
                                        for r in _coerce_answers(_load("answers.json", "answers"))])


def _forms_rows():
    return _store.table("forms").rows()


def _fields_rows():
    return _store.table("fields").rows()


def _responses_rows():
    return _store.table("responses").rows()


def _answers_rows():
    return [{k: v for k, v in r.items() if k != "_pk"} for r in _store.table("answers").rows()]



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _choices(raw):
    return [c.strip() for c in (raw or "").split("|") if c.strip()]


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_forms(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "is_public": strict_bool(r, "is_public"),
            "response_count": strict_int(r, "response_count"),
        })
    return out


def _coerce_fields(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "required": strict_bool(r, "required"),
            "choices": _choices(r["choices"]),
            "order": strict_int(r, "order"),
        })
    return out


def _coerce_responses(rows):
    return [{**_strip_ctx(r), "completed": strict_bool(r, "completed")} for r in rows]


def _coerce_answers(rows):
    return [{**_strip_ctx(r)} for r in rows]










def _new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------

def _field_obj(f):
    obj = {
        "id": f["field_id"],
        "title": f["title"],
        "ref": f["ref"],
        "type": f["field_type"],
        "required": f["required"],
    }
    if f["field_type"] == "multiple_choice":
        obj["properties"] = {"choices": [{"label": c} for c in f["choices"]]}
    return obj


def _form_obj(form):
    fields = sorted([f for f in _fields_rows() if f["form_id"] == form["form_id"]],
                    key=lambda f: f["order"])
    return {
        "id": form["form_id"],
        "title": form["title"],
        "language": form["language"],
        "workspace": {"href": f"https://api.typeform.com/workspaces/{form['workspace']}"},
        "settings": {"is_public": form["is_public"]},
        "fields": [_field_obj(f) for f in fields],
        "_links": {"display": f"https://orbitlabs.typeform.com/to/{form['form_id']}"},
        "created_at": form["created_time"],
        "last_updated_at": form["last_updated_time"],
    }


def _coerce_answer_value(field_type, raw):
    if field_type == "rating":
        try:
            return int(raw)
        except (TypeError, ValueError):
            return raw
    return raw


def _answer_obj(a):
    field_type = a["field_type"]
    value = _coerce_answer_value(field_type, a["answer"])
    obj = {
        "field": {"id": a["field_id"], "type": field_type, "ref": a["ref"]},
        "type": field_type,
    }
    if field_type == "multiple_choice":
        obj["choice"] = {"label": value}
    elif field_type == "rating":
        obj["number"] = value
    elif field_type == "email":
        obj["email"] = value
    else:
        obj["text"] = value
    return obj


def _response_obj(r):
    answers = [_answer_obj(a) for a in _answers_rows() if a["response_id"] == r["response_id"]]
    return {
        "response_id": r["response_id"],
        "landed_at": r["landed_time"],
        "submitted_at": r["submitted_time"],
        "answers": answers,
    }


def _find_form(form_id):
    return next((f for f in _forms_rows() if f["form_id"] == form_id), None)


# ---------------------------------------------------------------------------
# Forms
# ---------------------------------------------------------------------------

def list_forms():
    items = [{
        "id": f["form_id"],
        "title": f["title"],
        "last_updated_at": f["last_updated_time"],
        "_links": {"display": f"https://orbitlabs.typeform.com/to/{f['form_id']}"},
    } for f in _forms_rows()]
    return {
        "total_items": len(items),
        "page_count": 1,
        "items": items,
    }


def get_form(form_id):
    form = _find_form(form_id)
    if form is None:
        return {"error": f"form {form_id} not found"}
    return _form_obj(form)


def create_form(payload):
    form_id = _new_id("frm")
    now = _now()
    form = {
        "form_id": form_id,
        "title": payload.get("title", "Untitled form"),
        "workspace": payload.get("workspace", "ws-orbit-labs"),
        "language": payload.get("language", "en"),
        "is_public": bool(payload.get("is_public", False)),
        "response_count": 0,
        "created_time": now,
        "last_updated_time": now,
    }
    _store_insert("forms", form)
    for i, f in enumerate(payload.get("fields", []), start=1):
        _store_insert("fields", {
            "field_id": _new_id("fld"),
            "form_id": form_id,
            "title": f.get("title", ""),
            "field_type": f.get("type", "short_text"),
            "ref": f.get("ref", f"field_{i}"),
            "required": bool(f.get("required", False)),
            "choices": [c.get("label") if isinstance(c, dict) else c
                        for c in (f.get("properties", {}) or {}).get("choices", [])],
            "order": i,
        })
    return _form_obj(form)


def update_form(form_id, payload):
    form = _find_form(form_id)
    if form is None:
        return {"error": f"form {form_id} not found"}
    _changes = {}
    if "title" in payload:
        _changes["title"] = payload["title"]
    if "language" in payload:
        _changes["language"] = payload["language"]
    if "is_public" in payload:
        _changes["is_public"] = bool(payload["is_public"])
    _changes["last_updated_time"] = _now()
    form.update(_changes)
    _store_patch("forms", form, _changes)
    return _form_obj(form)


def delete_form(form_id):
    form = _find_form(form_id)
    if form is None:
        return {"error": f"form {form_id} not found"}
    _store_delete("forms", form)
    response_ids = [r["response_id"] for r in _responses_rows() if r["form_id"] == form_id]
    for f in [f for f in _fields_rows() if f["form_id"] == form_id]:
        _store_delete("fields", f)
    for r in [r for r in _responses_rows() if r["form_id"] == form_id]:
        _store_delete("responses", r)
    for a in [a for a in _answers_rows() if a["response_id"] in response_ids]:
        _store_delete("answers", a)
    return {"deleted": True, "id": form_id}


# ---------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------

def list_responses(form_id, completed=None):
    if _find_form(form_id) is None:
        return {"error": f"form {form_id} not found"}
    resp = [r for r in _responses_rows() if r["form_id"] == form_id]
    if completed is not None:
        resp = [r for r in resp if r["completed"] == completed]
    return {
        "total_items": len(resp),
        "page_count": 1,
        "items": [_response_obj(r) for r in resp],
    }


# ---------------------------------------------------------------------------
# Insights
# ---------------------------------------------------------------------------

def insights_summary(form_id):
    form = _find_form(form_id)
    if form is None:
        return {"error": f"form {form_id} not found"}
    resp = [r for r in _responses_rows() if r["form_id"] == form_id]
    total = len(resp)
    completed = len([r for r in resp if r["completed"]])
    fields = sorted([f for f in _fields_rows() if f["form_id"] == form_id],
                    key=lambda f: f["order"])
    field_summaries = []
    for f in fields:
        answers = [a for a in _answers_rows() if a["field_id"] == f["field_id"]]
        summary = {
            "field": {"id": f["field_id"], "title": f["title"], "type": f["field_type"]},
            "answer_count": len(answers),
        }
        if f["field_type"] == "rating":
            values = []
            for a in answers:
                try:
                    values.append(int(a["answer"]))
                except (TypeError, ValueError):
                    pass
            summary["average"] = round(sum(values) / len(values), 2) if values else None
        elif f["field_type"] == "multiple_choice":
            counts = {}
            for a in answers:
                counts[a["answer"]] = counts.get(a["answer"], 0) + 1
            summary["choices"] = counts
        field_summaries.append(summary)
    completion_rate = round(completed / total, 2) if total else 0.0
    return {
        "form": {"id": form_id, "title": form["title"]},
        "total_responses": total,
        "completed_responses": completed,
        "completion_rate": completion_rate,
        "fields": field_summaries,
    }

_store.eager_load()
