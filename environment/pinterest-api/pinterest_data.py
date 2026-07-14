"""Data access module for Pinterest API v5 simulation."""

import csv
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (  # noqa: E402
    read_seed_with_ctx, get_store, opt_str, strict_int)

_API = "pinterest-api"
_store = get_store("pinterest-api")
_API = "pinterest-api"



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

_store.register("boards", primary_key="board_id",
                initial_loader=lambda: _coerce_boards(_load("boards.json", "boards")))
_store.register("board_sections", primary_key="section_id",
                initial_loader=lambda: _coerce_board_sections(_load("board_sections.json", "board_sections")))
_store.register("pins", primary_key="pin_id",
                initial_loader=lambda: _coerce_pins(_load("pins.json", "pins")))
_store.register("pin_analytics", primary_key="_pk",
                initial_loader=lambda: [{**r, "_pk": f"{r['pin_id']}@{r['date']}"} for r in _coerce_pin_analytics(_load("pin_analytics.json", "pin_analytics"))])
_store.register("user_analytics", primary_key="date",
                initial_loader=lambda: _coerce_user_analytics(_load("user_analytics.json", "user_analytics")))
_store.register("ad_accounts", primary_key="ad_account_id",
                initial_loader=lambda: _coerce_ad_accounts(_load("ad_accounts.json", "ad_accounts")))
_store.register("campaigns", primary_key="campaign_id",
                initial_loader=lambda: _coerce_campaigns(_load("campaigns.json", "campaigns")))
_store.register_document("user_account_raw", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "user_account.json", encoding="utf-8")))


def _boards_rows():
    return _store.table("boards").rows()


def _board_sections_rows():
    return _store.table("board_sections").rows()


def _pins_rows():
    return _store.table("pins").rows()


def _pin_analytics_rows():
    return [{k: v for k, v in r.items() if k != "_pk"} for r in _store.table("pin_analytics").rows()]


def _user_analytics_rows():
    return _store.table("user_analytics").rows()


def _ad_accounts_rows():
    return _store.table("ad_accounts").rows()


def _campaigns_rows():
    return _store.table("campaigns").rows()


def _user_account_raw_doc():
    return _store.document("user_account_raw").get()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")


# ---------------------------------------------------------------------------
# Load and coerce data
# ---------------------------------------------------------------------------

def _coerce_boards(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "board_id": r["board_id"],
            "pin_count": strict_int(r, "pin_count"),
            "follower_count": strict_int(r, "follower_count"),
            "collaborator_count": strict_int(r, "collaborator_count"),
        })
    return out


def _coerce_board_sections(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "section_id": r["section_id"],
            "board_id": r["board_id"],
            "pin_count": strict_int(r, "pin_count"),
        })
    return out


def _coerce_pins(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "pin_id": r["pin_id"],
            "board_id": r["board_id"],
            "board_section_id": opt_str(r, "board_section_id", default="") or None,
            "link": opt_str(r, "link", default="") or None,
            "alt_text": opt_str(r, "alt_text", default="") or None,
            "is_promoted": r["is_promoted"].lower() == "true",
            "pin_metrics_impressions": strict_int(r, "pin_metrics_impressions"),
            "pin_metrics_saves": strict_int(r, "pin_metrics_saves"),
            "pin_metrics_clicks": strict_int(r, "pin_metrics_clicks"),
        })
    return out


def _coerce_pin_analytics(rows):
    out = []
    for r in rows:
        out.append({
            "pin_id": r["pin_id"],
            "date": r["date"],
            "impressions": strict_int(r, "impressions"),
            "saves": strict_int(r, "saves"),
            "pin_clicks": strict_int(r, "pin_clicks"),
            "outbound_clicks": strict_int(r, "outbound_clicks"),
        })
    return out


def _coerce_user_analytics(rows):
    out = []
    for r in rows:
        out.append({
            "date": r["date"],
            "impressions": strict_int(r, "impressions"),
            "saves": strict_int(r, "saves"),
            "pin_clicks": strict_int(r, "pin_clicks"),
            "outbound_clicks": strict_int(r, "outbound_clicks"),
            "profile_visits": strict_int(r, "profile_visits"),
            "follows": strict_int(r, "follows"),
        })
    return out


def _coerce_ad_accounts(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "ad_account_id": r["ad_account_id"],
        })
    return out


def _coerce_campaigns(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "campaign_id": r["campaign_id"],
            "ad_account_id": r["ad_account_id"],
            "daily_spend_cap_micro": strict_int(r, "daily_spend_cap_micro"),
            "lifetime_spend_cap_micro": strict_int(r, "lifetime_spend_cap_micro"),
            "end_time": opt_str(r, "end_time", default="") or None,
        })
    return out


# Load all data at module init









# Mutable in-memory stores








def _extract_numeric_id(id_str, prefix):
    """Extract numeric suffix from IDs like 'board_1001'. Returns 0 for non-numeric IDs."""
    stripped = id_str.replace(prefix, "", 1)
    try:
        return int(stripped)
    except (ValueError, TypeError):
        return 0


_store.eager_load()
_next_board_id = max(_extract_numeric_id(b["board_id"], "board_") for b in _boards_rows()) + 1
_next_section_id = max(_extract_numeric_id(s["section_id"], "section_") for s in _board_sections_rows()) + 1
_next_pin_id = max(_extract_numeric_id(p["pin_id"], "pin_") for p in _pins_rows()) + 1


# ---------------------------------------------------------------------------
# User Account
# ---------------------------------------------------------------------------

def get_user_account():
    raw = _store.document("user_account_raw").get()
    account = raw[0] if isinstance(raw, list) else raw
    return {"type": "user_account", "user_account": account}


def get_user_analytics(start_date=None, end_date=None):
    results = list(_user_analytics_rows())
    if start_date:
        results = [r for r in results if r["date"] >= start_date]
    if end_date:
        results = [r for r in results if r["date"] <= end_date]
    results = sorted(results, key=lambda x: x["date"])
    return {
        "type": "user_analytics",
        "count": len(results),
        "results": results,
    }


# ---------------------------------------------------------------------------
# Boards
# ---------------------------------------------------------------------------

def list_boards(privacy=None, limit=25, offset=0):
    results = list(_boards_rows())
    if privacy:
        results = [b for b in results if b["privacy"].upper() == privacy.upper()]
    results = sorted(results, key=lambda x: x["created_at"], reverse=True)
    total = len(results)
    page_results = results[offset: offset + limit]
    return {
        "type": "boards",
        "count": len(page_results),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page_results,
    }


def get_board(board_id: str):
    for b in _boards_rows():
        if b["board_id"] == board_id:
            return {"type": "board", "board": b}
    return {"error": f"Board {board_id} not found"}


def create_board(data: dict):
    global _next_board_id
    required = ["name"]
    for f in required:
        if f not in data or data[f] is None:
            return {"error": f"Missing required field: {f}"}

    now = _now()
    board = {
        "board_id": f"board_{_next_board_id}",
        "name": data["name"],
        "description": data.get("description", ""),
        "privacy": data.get("privacy", "PUBLIC"),
        "created_at": now,
        "updated_at": now,
        "pin_count": 0,
        "follower_count": 0,
        "collaborator_count": 0,
    }
    _store_insert("boards", board)
    _next_board_id += 1
    return {"type": "board", "board": board}


def update_board(board_id: str, data: dict):
    for board in _boards_rows():
        if board["board_id"] == board_id:
            updatable = {"name", "description", "privacy"}
            _changes = {}
            for k, v in data.items():
                if k in updatable:
                    _changes[k] = v
            _changes["updated_at"] = _now()
            board.update(_changes)
            _store_patch("boards", board, _changes)
            return {"type": "board", "board": board}
    return {"error": f"Board {board_id} not found"}


def delete_board(board_id: str):
    for board in _boards_rows():
        if board["board_id"] == board_id:
            _store_delete("boards", board)
            return {"type": "board", "deleted": True, "board_id": board_id}
    return {"error": f"Board {board_id} not found"}


def list_board_pins(board_id: str, limit=25, offset=0):
    # Check board exists
    if not any(b["board_id"] == board_id for b in _boards_rows()):
        return {"error": f"Board {board_id} not found"}
    results = [p for p in _pins_rows() if p["board_id"] == board_id]
    results = sorted(results, key=lambda x: x["created_at"], reverse=True)
    total = len(results)
    page_results = results[offset: offset + limit]
    return {
        "type": "pins",
        "count": len(page_results),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page_results,
    }


# ---------------------------------------------------------------------------
# Board Sections
# ---------------------------------------------------------------------------

def list_board_sections(board_id: str):
    if not any(b["board_id"] == board_id for b in _boards_rows()):
        return {"error": f"Board {board_id} not found"}
    sections = [s for s in _board_sections_rows() if s["board_id"] == board_id]
    return {"type": "board_sections", "count": len(sections), "results": sections}


def create_board_section(board_id: str, data: dict):
    global _next_section_id
    if not any(b["board_id"] == board_id for b in _boards_rows()):
        return {"error": f"Board {board_id} not found"}
    if "name" not in data or not data["name"]:
        return {"error": "Missing required field: name"}

    section = {
        "section_id": f"section_{_next_section_id}",
        "board_id": board_id,
        "name": data["name"],
        "pin_count": 0,
    }
    _store_insert("board_sections", section)
    _next_section_id += 1
    return {"type": "board_section", "board_section": section}


def list_section_pins(board_id: str, section_id: str, limit=25, offset=0):
    if not any(b["board_id"] == board_id for b in _boards_rows()):
        return {"error": f"Board {board_id} not found"}
    if not any(s["section_id"] == section_id and s["board_id"] == board_id for s in _board_sections_rows()):
        return {"error": f"Section {section_id} not found in board {board_id}"}
    results = [p for p in _pins_rows() if p["board_section_id"] == section_id]
    results = sorted(results, key=lambda x: x["created_at"], reverse=True)
    total = len(results)
    page_results = results[offset: offset + limit]
    return {
        "type": "pins",
        "count": len(page_results),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page_results,
    }


# ---------------------------------------------------------------------------
# Pins
# ---------------------------------------------------------------------------

def list_pins(limit=25, offset=0):
    results = sorted(_pins_rows(), key=lambda x: x["created_at"], reverse=True)
    total = len(results)
    page_results = results[offset: offset + limit]
    return {
        "type": "pins",
        "count": len(page_results),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page_results,
    }


def get_pin(pin_id: str):
    for p in _pins_rows():
        if p["pin_id"] == pin_id:
            return {"type": "pin", "pin": p}
    return {"error": f"Pin {pin_id} not found"}


def create_pin(data: dict):
    global _next_pin_id
    required = ["board_id", "title"]
    for f in required:
        if f not in data or data[f] is None:
            return {"error": f"Missing required field: {f}"}

    # Check board exists
    if not any(b["board_id"] == data["board_id"] for b in _boards_rows()):
        return {"error": f"Board {data['board_id']} not found"}

    now = _now()
    pin = {
        "pin_id": f"pin_{_next_pin_id}",
        "board_id": data["board_id"],
        "board_section_id": data.get("board_section_id"),
        "title": data["title"],
        "description": data.get("description", ""),
        "link": data.get("link"),
        "media_type": data.get("media_type", "image"),
        "created_at": now,
        "updated_at": now,
        "dominant_color": data.get("dominant_color", "#FFFFFF"),
        "alt_text": data.get("alt_text"),
        "is_promoted": False,
        "pin_metrics_impressions": 0,
        "pin_metrics_saves": 0,
        "pin_metrics_clicks": 0,
    }
    _store_insert("pins", pin)
    _next_pin_id += 1
    return {"type": "pin", "pin": pin}


def update_pin(pin_id: str, data: dict):
    for pin in _pins_rows():
        if pin["pin_id"] == pin_id:
            updatable = {"title", "description", "link", "board_id",
                         "board_section_id", "alt_text"}
            _changes = {}
            for k, v in data.items():
                if k in updatable:
                    _changes[k] = v
            _changes["updated_at"] = _now()
            pin.update(_changes)
            _store_patch("pins", pin, _changes)
            return {"type": "pin", "pin": pin}
    return {"error": f"Pin {pin_id} not found"}


def delete_pin(pin_id: str):
    for pin in _pins_rows():
        if pin["pin_id"] == pin_id:
            _store_delete("pins", pin)
            return {"type": "pin", "deleted": True, "pin_id": pin_id}
    return {"error": f"Pin {pin_id} not found"}


def get_pin_analytics(pin_id: str, start_date=None, end_date=None):
    # Check pin exists
    if not any(p["pin_id"] == pin_id for p in _pins_rows()):
        return {"error": f"Pin {pin_id} not found"}
    results = [a for a in _pin_analytics_rows() if a["pin_id"] == pin_id]
    if start_date:
        results = [r for r in results if r["date"] >= start_date]
    if end_date:
        results = [r for r in results if r["date"] <= end_date]
    results = sorted(results, key=lambda x: x["date"])
    return {
        "type": "pin_analytics",
        "count": len(results),
        "pin_id": pin_id,
        "results": results,
    }


def search_pins(query: str, limit=25, offset=0):
    q_lower = query.lower()
    results = [
        p for p in _pins_rows()
        if q_lower in p.get("title", "").lower()
        or q_lower in p.get("description", "").lower()
    ]
    results = sorted(results, key=lambda x: x["created_at"], reverse=True)
    total = len(results)
    page_results = results[offset: offset + limit]
    return {
        "type": "pins",
        "count": len(page_results),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page_results,
    }


# ---------------------------------------------------------------------------
# Media
# ---------------------------------------------------------------------------

def get_media_upload_status(media_id: str):
    # Mock: all existing pins have succeeded uploads
    if any(p["pin_id"] == media_id for p in _pins_rows()):
        return {
            "type": "media_upload",
            "media_id": media_id,
            "status": "succeeded",
            "media_type": "image",
        }
    return {"error": f"Media {media_id} not found"}


# ---------------------------------------------------------------------------
# Ad Accounts
# ---------------------------------------------------------------------------

def list_ad_accounts(limit=25, offset=0):
    results = list(_ad_accounts_rows())
    total = len(results)
    page_results = results[offset: offset + limit]
    return {
        "type": "ad_accounts",
        "count": len(page_results),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page_results,
    }


def get_ad_account(ad_account_id: str):
    for a in _ad_accounts_rows():
        if a["ad_account_id"] == ad_account_id:
            return {"type": "ad_account", "ad_account": a}
    return {"error": f"Ad account {ad_account_id} not found"}


def list_campaigns(ad_account_id: str, status=None, limit=25, offset=0):
    if not any(a["ad_account_id"] == ad_account_id for a in _ad_accounts_rows()):
        return {"error": f"Ad account {ad_account_id} not found"}
    results = [c for c in _campaigns_rows() if c["ad_account_id"] == ad_account_id]
    if status:
        results = [c for c in results if c["status"].upper() == status.upper()]
    total = len(results)
    page_results = results[offset: offset + limit]
    return {
        "type": "campaigns",
        "count": len(page_results),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page_results,
    }
