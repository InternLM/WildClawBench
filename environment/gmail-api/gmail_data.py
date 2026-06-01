"""Data access module for the Gmail API mock service."""

import csv
import json
import re
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now_ms():
    return int(datetime.utcnow().timestamp() * 1000)


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _coerce_labels(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "messagesTotal": int(r["messages_total"]),
            "messagesUnread": int(r["messages_unread"]),
            "threadsTotal": int(r["threads_total"]),
            "threadsUnread": int(r["threads_unread"]),
        })
    return out


def _coerce_messages(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "body": r["body"].replace("\\n", "\n"),
            "internal_date": int(r["internal_date"]),
            "size_estimate": int(r["size_estimate"]),
            "labels": [l for l in r["labels"].split(",") if l],
            "is_unread": _to_bool(r["is_unread"]),
            "is_starred": _to_bool(r["is_starred"]),
        })
    return out


def _coerce_drafts(rows):
    return [{**r, "body": r["body"].replace("\\n", "\n")} for r in rows]


_labels = _coerce_labels(_load("labels.csv"))
_messages = _coerce_messages(_load("messages.csv"))
_drafts = _coerce_drafts(_load("drafts.csv"))

with open(DATA_DIR / "profile.json", encoding="utf-8") as _f:
    _profile = json.load(_f)

_labels_store = deepcopy(_labels)
_messages_store = deepcopy(_messages)
_drafts_store = deepcopy(_drafts)
_profile_store = deepcopy(_profile)


def _new_id(prefix="msg"):
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


def _serialize_message(m, full=True):
    out = {
        "id": m["id"],
        "threadId": m["thread_id"],
        "labelIds": m["labels"],
        "snippet": m["snippet"],
        "internalDate": str(m["internal_date"]),
        "sizeEstimate": m["size_estimate"],
    }
    if full:
        out["payload"] = {
            "headers": [
                {"name": "From", "value": m["from_addr"]},
                {"name": "To", "value": m["to_addr"]},
                {"name": "Cc", "value": m["cc_addr"]},
                {"name": "Subject", "value": m["subject"]},
                {"name": "Date", "value": m["date"]},
            ],
            "body": {"data": m["body"], "size": len(m["body"])},
            "mimeType": "text/plain",
        }
    return out


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

def get_profile():
    return _profile_store


# ---------------------------------------------------------------------------
# Labels
# ---------------------------------------------------------------------------

def list_labels():
    return {"labels": [{"id": l["id"], "name": l["name"], "type": l["type"]} for l in _labels_store]}


def get_label(label_id):
    for l in _labels_store:
        if l["id"] == label_id:
            return l
    return {"error": f"Label {label_id} not found"}


def create_label(name):
    if any(l["name"] == name for l in _labels_store):
        return {"error": f"Label {name} already exists"}
    label = {
        "id": f"Label_{uuid.uuid4().hex[:8]}",
        "name": name,
        "type": "user",
        "messages_total": 0, "messagesTotal": 0,
        "messages_unread": 0, "messagesUnread": 0,
        "threads_total": 0, "threadsTotal": 0,
        "threads_unread": 0, "threadsUnread": 0,
    }
    _labels_store.append(label)
    return label


# ---------------------------------------------------------------------------
# Messages / threads
# ---------------------------------------------------------------------------

_QUERY_KV = re.compile(r"(\w+):(\"[^\"]*\"|\S+)")


def _parse_query(query):
    filters = {}
    free_text = query
    for m in _QUERY_KV.finditer(query):
        key = m.group(1).lower()
        val = m.group(2).strip('"')
        filters.setdefault(key, []).append(val)
        free_text = free_text.replace(m.group(0), "")
    free_text = free_text.strip()
    return filters, free_text


def list_messages(query="", max_results=25, label_ids=None):
    label_ids = label_ids or []
    filters, free_text = _parse_query(query or "")
    results = list(_messages_store)
    if label_ids:
        results = [m for m in results if all(l in m["labels"] for l in label_ids)]
    if "from" in filters:
        results = [m for m in results if any(f.lower() in m["from_addr"].lower() for f in filters["from"])]
    if "to" in filters:
        results = [m for m in results if any(f.lower() in m["to_addr"].lower() for f in filters["to"])]
    if "subject" in filters:
        results = [m for m in results if any(f.lower() in m["subject"].lower() for f in filters["subject"])]
    if "label" in filters:
        # name-based label match
        for lname in filters["label"]:
            ids = {l["id"] for l in _labels_store if l["name"].lower() == lname.lower()}
            results = [m for m in results if ids & set(m["labels"])]
    if "is" in filters:
        if "unread" in [v.lower() for v in filters["is"]]:
            results = [m for m in results if m["is_unread"]]
        if "starred" in [v.lower() for v in filters["is"]]:
            results = [m for m in results if m["is_starred"]]
    if free_text:
        ft = free_text.lower()
        results = [m for m in results
                   if ft in m["subject"].lower() or ft in m["body"].lower() or ft in m["snippet"].lower()]
    results.sort(key=lambda m: m["internal_date"], reverse=True)
    page = results[:max_results]
    return {"messages": [{"id": m["id"], "threadId": m["thread_id"]} for m in page],
            "resultSizeEstimate": len(results)}


def get_message(message_id, fmt="full"):
    for m in _messages_store:
        if m["id"] == message_id:
            return _serialize_message(m, full=(fmt == "full"))
    return {"error": f"Message {message_id} not found"}


def send_message(to_addr, subject, body, cc=None, thread_id=None,
                 from_addr=None):
    msg_id = _new_id("msg")
    thread_id = thread_id or f"thr-{uuid.uuid4().hex[:8]}"
    now = _now_ms()
    msg = {
        "id": msg_id,
        "thread_id": thread_id,
        "from_addr": from_addr or _profile_store["emailAddress"],
        "to_addr": to_addr,
        "cc_addr": cc or "",
        "subject": subject,
        "snippet": (body[:140] + "...") if len(body) > 140 else body,
        "body": body,
        "date": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "internal_date": now,
        "size_estimate": len(body) + len(subject),
        "labels": ["SENT"],
        "is_unread": False,
        "is_starred": False,
    }
    _messages_store.append(msg)
    return _serialize_message(msg)


def modify_message(message_id, add_labels=None, remove_labels=None):
    for i, m in enumerate(_messages_store):
        if m["id"] == message_id:
            labels = set(m["labels"])
            if add_labels:
                labels.update(add_labels)
            if remove_labels:
                labels.difference_update(remove_labels)
            _messages_store[i]["labels"] = sorted(labels)
            if "UNREAD" in (remove_labels or []):
                _messages_store[i]["is_unread"] = False
            if "STARRED" in (add_labels or []):
                _messages_store[i]["is_starred"] = True
            if "STARRED" in (remove_labels or []):
                _messages_store[i]["is_starred"] = False
            return _serialize_message(_messages_store[i])
    return {"error": f"Message {message_id} not found"}


def trash_message(message_id):
    return modify_message(message_id, add_labels=["TRASH"], remove_labels=["INBOX"])


def delete_message(message_id):
    for i, m in enumerate(_messages_store):
        if m["id"] == message_id:
            _messages_store.pop(i)
            return {"deleted": True, "id": message_id}
    return {"error": f"Message {message_id} not found"}


def list_threads(query=""):
    msg_list = list_messages(query=query)
    seen = []
    for entry in msg_list["messages"]:
        if entry["threadId"] not in [s["id"] for s in seen]:
            seen.append({"id": entry["threadId"]})
    return {"threads": seen, "resultSizeEstimate": len(seen)}


def get_thread(thread_id):
    msgs = [m for m in _messages_store if m["thread_id"] == thread_id]
    if not msgs:
        return {"error": f"Thread {thread_id} not found"}
    msgs.sort(key=lambda m: m["internal_date"])
    return {
        "id": thread_id,
        "historyId": _profile_store["historyId"],
        "messages": [_serialize_message(m) for m in msgs],
    }


# ---------------------------------------------------------------------------
# Drafts
# ---------------------------------------------------------------------------

def list_drafts():
    return {"drafts": [{"id": d["id"], "message": {"id": "", "threadId": d["thread_id"]}}
                       for d in _drafts_store]}


def get_draft(draft_id):
    for d in _drafts_store:
        if d["id"] == draft_id:
            return d
    return {"error": f"Draft {draft_id} not found"}


def create_draft(to_addr, subject, body, cc=None, thread_id=None):
    draft = {
        "id": _new_id("draft"),
        "thread_id": thread_id or "",
        "to_addr": to_addr,
        "cc_addr": cc or "",
        "subject": subject,
        "body": body,
        "updated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    _drafts_store.append(draft)
    return draft


def send_draft(draft_id):
    draft = next((d for d in _drafts_store if d["id"] == draft_id), None)
    if not draft:
        return {"error": f"Draft {draft_id} not found"}
    sent = send_message(
        to_addr=draft["to_addr"],
        subject=draft["subject"],
        body=draft["body"],
        cc=draft["cc_addr"],
        thread_id=draft["thread_id"] or None,
    )
    _drafts_store.remove(draft)
    return sent
