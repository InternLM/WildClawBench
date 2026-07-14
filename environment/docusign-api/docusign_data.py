"""Data access module for the DocuSign eSignature API mock service."""

import csv
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (  # noqa: E402
    read_seed_with_ctx, get_store, opt_str, strict_bool, strict_int)

_store = get_store("docusign-api")
_API = "docusign-api"


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

_store.register("envelopes", primary_key="envelope_id",
                initial_loader=lambda: _coerce_envelopes(_load("envelopes.json", "envelopes")))
_store.register("recipients", primary_key="recipient_id",
                initial_loader=lambda: _coerce_recipients(_load("recipients.json", "recipients")))
_store.register("documents", primary_key="document_id",
                initial_loader=lambda: _coerce_documents(_load("documents.json", "documents")))
_store.register("templates", primary_key="template_id",
                initial_loader=lambda: _coerce_templates(_load("templates.json", "templates")))


def _envelopes_rows():
    return _store.table("envelopes").rows()


def _recipients_rows():
    return _store.table("recipients").rows()


def _documents_rows():
    return _store.table("documents").rows()


def _templates_rows():
    return _store.table("templates").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.0000000Z")


def _to_bool(v):
    return str(v).strip().lower() == "true"


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_envelopes(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "sent_time": opt_str(r, "sent_time", default="") or None,
            "completed_time": opt_str(r, "completed_time", default="") or None,
            "template_id": opt_str(r, "template_id", default="") or None,
        })
    return out


def _coerce_recipients(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "routing_order": strict_int(r, "routing_order"),
            "signed_time": opt_str(r, "signed_time", default="") or None,
        })
    return out


def _coerce_documents(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "page_count": strict_int(r, "page_count"),
            "order": strict_int(r, "order"),
        })
    return out


def _coerce_templates(rows):
    return [{**_strip_ctx(r), "shared": strict_bool(r, "shared")} for r in rows]










def _new_envelope_id():
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Serializers (DocuSign-style camelCase)
# ---------------------------------------------------------------------------

def _envelope_obj(e):
    return {
        "envelopeId": e["envelope_id"],
        "status": e["status"],
        "emailSubject": e["email_subject"],
        "sender": {"userName": e["sender_name"], "email": e["sender_email"]},
        "createdDateTime": e["created_time"],
        "sentDateTime": e["sent_time"],
        "completedDateTime": e["completed_time"],
        "templateId": e["template_id"],
    }


def _recipient_obj(r):
    return {
        "recipientId": r["recipient_id"],
        "name": r["name"],
        "email": r["email"],
        "recipientType": r["recipient_type"],
        "status": r["status"],
        "routingOrder": r["routing_order"],
        "signedDateTime": r["signed_time"],
    }


def _document_obj(d):
    return {
        "documentId": d["document_id"],
        "name": d["name"],
        "type": d["document_type"],
        "pages": d["page_count"],
        "order": d["order"],
    }


def _template_obj(t):
    return {
        "templateId": t["template_id"],
        "name": t["name"],
        "description": t["description"],
        "shared": "true" if t["shared"] else "false",
        "owner": {"userName": t["owner_name"]},
        "created": t["created_time"],
    }


def _find_envelope(envelope_id):
    return next((e for e in _envelopes_rows() if e["envelope_id"] == envelope_id), None)


# ---------------------------------------------------------------------------
# Envelopes
# ---------------------------------------------------------------------------

def list_envelopes(status=None):
    envs = _envelopes_rows()
    if status:
        envs = [e for e in envs if e["status"].lower() == status.lower()]
    return {
        "resultSetSize": str(len(envs)),
        "totalSetSize": str(len(envs)),
        "envelopes": [_envelope_obj(e) for e in envs],
    }


def get_envelope(envelope_id):
    e = _find_envelope(envelope_id)
    if e is None:
        return {"error": f"envelope {envelope_id} not found"}
    return _envelope_obj(e)


def create_envelope(payload):
    status = (payload.get("status") or "created").lower()
    now = _now()
    envelope_id = _new_envelope_id()
    env = {
        "envelope_id": envelope_id,
        "status": status,
        "email_subject": payload.get("emailSubject", ""),
        "sender_name": payload.get("senderName", "Amelia Ortega"),
        "sender_email": payload.get("senderEmail", "amelia.ortega@orbit-labs.com"),
        "created_time": now,
        "sent_time": now if status == "sent" else None,
        "completed_time": None,
        "template_id": payload.get("templateId") or None,
    }
    _store_insert("envelopes", env)

    for i, r in enumerate(payload.get("recipients", {}).get("signers", []), start=1):
        _store_insert("recipients", {
            "recipient_id": r.get("recipientId") or str(i),
            "envelope_id": envelope_id,
            "name": r.get("name", ""),
            "email": r.get("email", ""),
            "recipient_type": "signer",
            "status": "sent" if status == "sent" else "created",
            "routing_order": int(r.get("routingOrder", i)),
            "signed_time": None,
        })

    for i, d in enumerate(payload.get("documents", []), start=1):
        _store_insert("documents", {
            "document_id": d.get("documentId") or str(i),
            "envelope_id": envelope_id,
            "name": d.get("name", f"document-{i}.pdf"),
            "document_type": "content",
            "page_count": int(d.get("pages", 1)),
            "order": i,
        })
    return {"envelopeId": envelope_id, "status": status,
            "statusDateTime": now, "uri": f"/envelopes/{envelope_id}"}


def update_envelope(envelope_id, status):
    e = _find_envelope(envelope_id)
    if e is None:
        return {"error": f"envelope {envelope_id} not found"}
    status = status.lower()
    e["status"] = status
    now = _now()
    if status == "sent" and not e["sent_time"]:
        e["sent_time"] = now
    if status == "completed":
        e["completed_time"] = now
    return {"envelopeId": envelope_id, "status": status, "statusDateTime": now}


# ---------------------------------------------------------------------------
# Recipients / documents
# ---------------------------------------------------------------------------

def list_recipients(envelope_id):
    if _find_envelope(envelope_id) is None:
        return {"error": f"envelope {envelope_id} not found"}
    signers = [r for r in _recipients_rows() if r["envelope_id"] == envelope_id]
    signers = sorted(signers, key=lambda r: r["routing_order"])
    return {
        "signers": [_recipient_obj(r) for r in signers],
        "recipientCount": str(len(signers)),
    }


def list_documents(envelope_id):
    if _find_envelope(envelope_id) is None:
        return {"error": f"envelope {envelope_id} not found"}
    docs = [d for d in _documents_rows() if d["envelope_id"] == envelope_id]
    docs = sorted(docs, key=lambda d: d["order"])
    return {"envelopeId": envelope_id,
            "envelopeDocuments": [_document_obj(d) for d in docs]}


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

def list_templates():
    return {
        "resultSetSize": str(len(_templates_rows())),
        "envelopeTemplates": [_template_obj(t) for t in _templates_rows()],
    }

_store.eager_load()
