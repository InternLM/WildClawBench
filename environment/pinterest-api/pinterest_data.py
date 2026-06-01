"""Data access module for Pinterest API v5 simulation."""

import csv
import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")


# ---------------------------------------------------------------------------
# Load and coerce data
# ---------------------------------------------------------------------------

def _coerce_boards(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "board_id": r["board_id"],
            "pin_count": int(r["pin_count"]),
            "follower_count": int(r["follower_count"]),
            "collaborator_count": int(r["collaborator_count"]),
        })
    return out


def _coerce_board_sections(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "section_id": r["section_id"],
            "board_id": r["board_id"],
            "pin_count": int(r["pin_count"]),
        })
    return out


def _coerce_pins(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "pin_id": r["pin_id"],
            "board_id": r["board_id"],
            "board_section_id": r["board_section_id"] if r["board_section_id"] else None,
            "link": r["link"] if r["link"] else None,
            "alt_text": r["alt_text"] if r["alt_text"] else None,
            "is_promoted": r["is_promoted"].lower() == "true",
            "pin_metrics_impressions": int(r["pin_metrics_impressions"]),
            "pin_metrics_saves": int(r["pin_metrics_saves"]),
            "pin_metrics_clicks": int(r["pin_metrics_clicks"]),
        })
    return out


def _coerce_pin_analytics(rows):
    out = []
    for r in rows:
        out.append({
            "pin_id": r["pin_id"],
            "date": r["date"],
            "impressions": int(r["impressions"]),
            "saves": int(r["saves"]),
            "pin_clicks": int(r["pin_clicks"]),
            "outbound_clicks": int(r["outbound_clicks"]),
        })
    return out


def _coerce_user_analytics(rows):
    out = []
    for r in rows:
        out.append({
            "date": r["date"],
            "impressions": int(r["impressions"]),
            "saves": int(r["saves"]),
            "pin_clicks": int(r["pin_clicks"]),
            "outbound_clicks": int(r["outbound_clicks"]),
            "profile_visits": int(r["profile_visits"]),
            "follows": int(r["follows"]),
        })
    return out


def _coerce_ad_accounts(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "ad_account_id": r["ad_account_id"],
        })
    return out


def _coerce_campaigns(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "campaign_id": r["campaign_id"],
            "ad_account_id": r["ad_account_id"],
            "daily_spend_cap_micro": int(r["daily_spend_cap_micro"]),
            "lifetime_spend_cap_micro": int(r["lifetime_spend_cap_micro"]),
            "end_time": r["end_time"] if r["end_time"] else None,
        })
    return out


# Load all data at module init
_boards = _coerce_boards(_load("boards.csv"))
_board_sections = _coerce_board_sections(_load("board_sections.csv"))
_pins = _coerce_pins(_load("pins.csv"))
_pin_analytics = _coerce_pin_analytics(_load("pin_analytics.csv"))
_user_analytics = _coerce_user_analytics(_load("user_analytics.csv"))
_ad_accounts = _coerce_ad_accounts(_load("ad_accounts.csv"))
_campaigns = _coerce_campaigns(_load("campaigns.csv"))

with open(DATA_DIR / "user_account.json", encoding="utf-8") as _f:
    _user_account_raw = json.load(_f)
    # user_account.json may be a single account dict or a list of accounts.
    # Use the first account as the active user.
    _user_account = _user_account_raw[0] if isinstance(_user_account_raw, list) else _user_account_raw

# Mutable in-memory stores
_boards_store = deepcopy(_boards)
_board_sections_store = deepcopy(_board_sections)
_pins_store = deepcopy(_pins)
_pin_analytics_store = deepcopy(_pin_analytics)
_user_analytics_store = deepcopy(_user_analytics)
_ad_accounts_store = deepcopy(_ad_accounts)
_campaigns_store = deepcopy(_campaigns)
_user_account_store = deepcopy(_user_account)

def _extract_numeric_id(id_str, prefix):
    """Extract numeric suffix from IDs like 'board_1001'. Returns 0 for non-numeric IDs."""
    stripped = id_str.replace(prefix, "", 1)
    try:
        return int(stripped)
    except (ValueError, TypeError):
        return 0


_next_board_id = max(_extract_numeric_id(b["board_id"], "board_") for b in _boards_store) + 1
_next_section_id = max(_extract_numeric_id(s["section_id"], "section_") for s in _board_sections_store) + 1
_next_pin_id = max(_extract_numeric_id(p["pin_id"], "pin_") for p in _pins_store) + 1


# ---------------------------------------------------------------------------
# User Account
# ---------------------------------------------------------------------------

def get_user_account():
    return {"type": "user_account", "user_account": _user_account_store}


def get_user_analytics(start_date=None, end_date=None):
    results = list(_user_analytics_store)
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
    results = list(_boards_store)
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
    for b in _boards_store:
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
    _boards_store.append(board)
    _next_board_id += 1
    return {"type": "board", "board": board}


def update_board(board_id: str, data: dict):
    for i, board in enumerate(_boards_store):
        if board["board_id"] == board_id:
            updatable = {"name", "description", "privacy"}
            for k, v in data.items():
                if k in updatable:
                    _boards_store[i][k] = v
            _boards_store[i]["updated_at"] = _now()
            return {"type": "board", "board": _boards_store[i]}
    return {"error": f"Board {board_id} not found"}


def delete_board(board_id: str):
    for i, board in enumerate(_boards_store):
        if board["board_id"] == board_id:
            _boards_store.pop(i)
            return {"type": "board", "deleted": True, "board_id": board_id}
    return {"error": f"Board {board_id} not found"}


def list_board_pins(board_id: str, limit=25, offset=0):
    # Check board exists
    if not any(b["board_id"] == board_id for b in _boards_store):
        return {"error": f"Board {board_id} not found"}
    results = [p for p in _pins_store if p["board_id"] == board_id]
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
    if not any(b["board_id"] == board_id for b in _boards_store):
        return {"error": f"Board {board_id} not found"}
    sections = [s for s in _board_sections_store if s["board_id"] == board_id]
    return {"type": "board_sections", "count": len(sections), "results": sections}


def create_board_section(board_id: str, data: dict):
    global _next_section_id
    if not any(b["board_id"] == board_id for b in _boards_store):
        return {"error": f"Board {board_id} not found"}
    if "name" not in data or not data["name"]:
        return {"error": "Missing required field: name"}

    section = {
        "section_id": f"section_{_next_section_id}",
        "board_id": board_id,
        "name": data["name"],
        "pin_count": 0,
    }
    _board_sections_store.append(section)
    _next_section_id += 1
    return {"type": "board_section", "board_section": section}


def list_section_pins(board_id: str, section_id: str, limit=25, offset=0):
    if not any(b["board_id"] == board_id for b in _boards_store):
        return {"error": f"Board {board_id} not found"}
    if not any(s["section_id"] == section_id and s["board_id"] == board_id for s in _board_sections_store):
        return {"error": f"Section {section_id} not found in board {board_id}"}
    results = [p for p in _pins_store if p["board_section_id"] == section_id]
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
    results = sorted(_pins_store, key=lambda x: x["created_at"], reverse=True)
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
    for p in _pins_store:
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
    if not any(b["board_id"] == data["board_id"] for b in _boards_store):
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
    _pins_store.append(pin)
    _next_pin_id += 1
    return {"type": "pin", "pin": pin}


def update_pin(pin_id: str, data: dict):
    for i, pin in enumerate(_pins_store):
        if pin["pin_id"] == pin_id:
            updatable = {"title", "description", "link", "board_id",
                         "board_section_id", "alt_text"}
            for k, v in data.items():
                if k in updatable:
                    _pins_store[i][k] = v
            _pins_store[i]["updated_at"] = _now()
            return {"type": "pin", "pin": _pins_store[i]}
    return {"error": f"Pin {pin_id} not found"}


def delete_pin(pin_id: str):
    for i, pin in enumerate(_pins_store):
        if pin["pin_id"] == pin_id:
            _pins_store.pop(i)
            return {"type": "pin", "deleted": True, "pin_id": pin_id}
    return {"error": f"Pin {pin_id} not found"}


def get_pin_analytics(pin_id: str, start_date=None, end_date=None):
    # Check pin exists
    if not any(p["pin_id"] == pin_id for p in _pins_store):
        return {"error": f"Pin {pin_id} not found"}
    results = [a for a in _pin_analytics_store if a["pin_id"] == pin_id]
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
        p for p in _pins_store
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
    if any(p["pin_id"] == media_id for p in _pins_store):
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
    results = list(_ad_accounts_store)
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
    for a in _ad_accounts_store:
        if a["ad_account_id"] == ad_account_id:
            return {"type": "ad_account", "ad_account": a}
    return {"error": f"Ad account {ad_account_id} not found"}


def list_campaigns(ad_account_id: str, status=None, limit=25, offset=0):
    if not any(a["ad_account_id"] == ad_account_id for a in _ad_accounts_store):
        return {"error": f"Ad account {ad_account_id} not found"}
    results = [c for c in _campaigns_store if c["ad_account_id"] == ad_account_id]
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
