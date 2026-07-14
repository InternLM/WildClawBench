"""Data access module for the FedEx API mock service.

Mirrors a subset of the FedEx Web Services REST APIs: rate quotes,
shipment (label) creation, and tracking. Responses use FedEx-style
`{"output": {...}}` envelopes.
"""

import csv
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store,
    strict_int,
    opt_float,
)

_store = get_store("fedex-api")
_API = "fedex-api"


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

# rates natural key (service_type, origin_zip, dest_zip, weight_lb) -> synth composite pk
_store.register("rates", primary_key="_pk",
                initial_loader=lambda: [
                    {**r, "_pk": f"{r['service_type']}@{r['origin_zip']}@{r['dest_zip']}@{r['weight_lb']}"}
                    for r in _coerce_rates(_load("rates.json", "rates"))])
_store.register("shipments", primary_key="tracking_number",
                initial_loader=lambda: _coerce_shipments(_load("shipments.json", "shipments")))
_store.register("tracking", primary_key="tracking_number",
                initial_loader=lambda: _coerce_tracking(_load("tracking.json", "tracking")))


def _rates_rows():
    return [{k: v for k, v in r.items() if k != "_pk"} for r in _store.table("rates").rows()]


def _shipments_rows():
    return _store.table("shipments").rows()


def _tracking_rows():
    return _store.table("tracking").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_rates(rows):
    out = []
    for r in rows:
        out.append({
            "service_type": r["service_type"],
            "service_name": r["service_name"],
            "origin_zip": r["origin_zip"],
            "dest_zip": r["dest_zip"],
            "weight_lb": opt_float(r, "weight_lb", default=None),
            "currency": r["currency"],
            "net_charge": opt_float(r, "net_charge", default=None),
            "transit_days": strict_int(r, "transit_days"),
            "delivery_day": r["delivery_day"],
        })
    return out


def _coerce_shipments(rows):
    out = []
    for r in rows:
        out.append({
            "tracking_number": r["tracking_number"],
            "service_type": r["service_type"],
            "service_name": r["service_name"],
            "ship_date": r["ship_date"],
            "origin_zip": r["origin_zip"],
            "dest_zip": r["dest_zip"],
            "weight_lb": opt_float(r, "weight_lb", default=None),
            "currency": r["currency"],
            "net_charge": opt_float(r, "net_charge", default=None),
            "label_url": r["label_url"],
        })
    return out


def _coerce_tracking(rows):
    out = []
    for r in rows:
        out.append({
            "tracking_number": r["tracking_number"],
            "status_code": r["status_code"],
            "status_description": r["status_description"],
            "carrier_code": r["carrier_code"],
            "service_name": r["service_name"],
            "ship_date": r["ship_date"],
            "estimated_delivery": r["estimated_delivery"],
            "latest_event": r["latest_event"],
            "latest_event_location": r["latest_event_location"],
            "latest_event_time": r["latest_event_time"],
        })
    return out








# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_tracking_number():
    base = max((int(s["tracking_number"]) for s in _shipments_rows()), default=794612035840)
    return str(base + 11)


def _today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Rate quotes  (POST /rate/v1/rates/quotes)
# ---------------------------------------------------------------------------

def get_rate_quote(origin_zip, dest_zip, weight_lb, service_type=None):
    matches = [
        r for r in _rates_rows()
        if r["origin_zip"] == str(origin_zip) and r["dest_zip"] == str(dest_zip)
    ]
    if service_type:
        matches = [r for r in matches if r["service_type"] == service_type]
    if not matches:
        return {"error": f"no rates found for {origin_zip} -> {dest_zip}"}
    weight = _to_float(weight_lb) or 1.0
    details = []
    for r in matches:
        base = r["net_charge"]
        scaled = round(base * (weight / (r["weight_lb"] or 1.0)), 2) if r["weight_lb"] else base
        details.append({
            "serviceType": r["service_type"],
            "serviceName": r["service_name"],
            "packagingType": "YOUR_PACKAGING",
            "commit": {
                "dateDetail": {"dayCxsFormat": r["delivery_day"]},
                "transitDays": r["transit_days"],
            },
            "ratedShipmentDetails": [{
                "rateType": "ACCOUNT",
                "totalNetCharge": scaled,
                "currency": r["currency"],
            }],
        })
    return {"output": {"rateReplyDetails": details, "quoteDate": _today()}}


# ---------------------------------------------------------------------------
# Shipments  (POST /ship/v1/shipments)
# ---------------------------------------------------------------------------

def create_shipment(origin_zip, dest_zip, weight_lb, service_type="FEDEX_GROUND"):
    rate = next(
        (r for r in _rates_rows()
         if r["origin_zip"] == str(origin_zip)
         and r["dest_zip"] == str(dest_zip)
         and r["service_type"] == service_type),
        None,
    )
    net_charge = rate["net_charge"] if rate else 0.0
    currency = rate["currency"] if rate else "USD"
    service_name = rate["service_name"] if rate else service_type.replace("_", " ").title()
    tracking_number = _new_tracking_number()
    label_url = f"https://fedex.example/labels/{tracking_number}.pdf"
    shipment = {
        "tracking_number": tracking_number,
        "service_type": service_type,
        "service_name": service_name,
        "ship_date": _today(),
        "origin_zip": str(origin_zip),
        "dest_zip": str(dest_zip),
        "weight_lb": _to_float(weight_lb),
        "currency": currency,
        "net_charge": net_charge,
        "label_url": label_url,
    }
    _store_insert("shipments", shipment)
    _store_insert("tracking", {
        "tracking_number": tracking_number,
        "status_code": "PU",
        "status_description": "Picked up",
        "carrier_code": "FDXG" if "GROUND" in service_type else "FDXE",
        "service_name": service_name,
        "ship_date": shipment["ship_date"],
        "estimated_delivery": (datetime.now(timezone.utc) + timedelta(days=(rate["transit_days"] if rate else 3))).strftime("%Y-%m-%d"),
        "latest_event": "Shipment information sent to FedEx",
        "latest_event_location": str(origin_zip),
        "latest_event_time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    })
    return {
        "output": {
            "transactionShipments": [{
                "serviceType": service_type,
                "serviceName": service_name,
                "shipDatestamp": shipment["ship_date"],
                "masterTrackingNumber": tracking_number,
                "pieceResponses": [{
                    "trackingNumber": tracking_number,
                    "netChargeAmount": net_charge,
                    "currency": currency,
                    "packageDocuments": [{
                        "contentType": "LABEL",
                        "docType": "PDF",
                        "url": label_url,
                    }],
                }],
            }],
        }
    }


# ---------------------------------------------------------------------------
# Tracking  (POST /track/v1/trackingnumbers)
# ---------------------------------------------------------------------------

def track(tracking_number):
    t = next((x for x in _tracking_rows() if x["tracking_number"] == str(tracking_number)), None)
    if not t:
        return {"error": f"tracking number {tracking_number} not found"}
    return {
        "output": {
            "completeTrackResults": [{
                "trackingNumber": t["tracking_number"],
                "trackResults": [{
                    "trackingNumberInfo": {
                        "trackingNumber": t["tracking_number"],
                        "carrierCode": t["carrier_code"],
                    },
                    "latestStatusDetail": {
                        "code": t["status_code"],
                        "description": t["status_description"],
                        "scanLocation": {"city": t["latest_event_location"]},
                    },
                    "serviceDetail": {"description": t["service_name"]},
                    "dateAndTimes": [
                        {"type": "SHIP", "dateTime": t["ship_date"]},
                        {"type": "ESTIMATED_DELIVERY", "dateTime": t["estimated_delivery"]},
                    ],
                    "scanEvents": [{
                        "date": t["latest_event_time"],
                        "eventDescription": t["latest_event"],
                        "scanLocation": {"city": t["latest_event_location"]},
                    }],
                }],
            }],
        }
    }

_store.eager_load()
