"""End-to-end smoke test for the drift plane.

Spins up the kraken-api FastAPI app via TestClient with MOCK_ADMIN_ENABLED=1
and verifies that admin-plane mutations are reflected in subsequent reads
through the public API. Run with:

    pytest tests/test_drift_plane_smoke.py -v
"""

import os
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
KRAKEN_DIR = REPO_ROOT / "environment" / "kraken-api"
ENV_DIR = REPO_ROOT / "environment"


@pytest.fixture
def admin_client(monkeypatch):
    monkeypatch.setenv("MOCK_ADMIN_ENABLED", "1")
    monkeypatch.setenv("MOCK_ADMIN_ALLOWLIST", "127.0.0.1,testclient")

    monkeypatch.syspath_prepend(str(ENV_DIR))
    monkeypatch.syspath_prepend(str(KRAKEN_DIR))

    for mod in [
        "kraken_data", "server", "_mutable_store", "admin_plane",
        "tracking_middleware",
    ]:
        sys.modules.pop(mod, None)

    import server  # type: ignore
    from fastapi.testclient import TestClient

    yield TestClient(server.app)

    for mod in [
        "kraken_data", "server", "_mutable_store", "admin_plane",
        "tracking_middleware",
    ]:
        sys.modules.pop(mod, None)


def test_admin_health_reachable(admin_client):
    r = admin_client.get("/admin/health")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert "tickers" in body["tables"]


def test_admin_blocks_unallowlisted_ip(monkeypatch):
    monkeypatch.setenv("MOCK_ADMIN_ENABLED", "1")
    monkeypatch.setenv("MOCK_ADMIN_ALLOWLIST", "10.99.99.99")
    monkeypatch.syspath_prepend(str(ENV_DIR))
    monkeypatch.syspath_prepend(str(KRAKEN_DIR))
    for mod in [
        "kraken_data", "server", "_mutable_store", "admin_plane",
        "tracking_middleware",
    ]:
        sys.modules.pop(mod, None)

    import server  # type: ignore
    from fastapi.testclient import TestClient

    client = TestClient(server.app)
    r = client.get("/admin/health")
    assert r.status_code == 404


def test_data_patch_visible_in_public_endpoint(admin_client):
    r = admin_client.get("/admin/data/balances")
    assert r.status_code == 200
    rows = r.json()["rows"]
    assert rows, "expected pre-loaded balances"
    target = rows[0]
    asset = target["asset"]

    r = admin_client.patch(
        f"/admin/data/balances/{asset}",
        json={"fields": {"balance": "999999.99999"}},
    )
    assert r.status_code == 200, r.text

    r = admin_client.post("/0/private/Balance")
    assert r.status_code == 200
    public = r.json()["result"]
    assert public[asset] == "999999.99999"


def test_snapshot_restore_round_trip(admin_client):
    r = admin_client.get("/admin/data/balances")
    original = r.json()["rows"][0]
    asset = original["asset"]
    pristine_balance = original["balance"]

    r = admin_client.get("/admin/snapshot/__baseline__")
    if r.status_code == 404:
        r = admin_client.get("/admin/snapshot", params={"label": "pristine"})
        assert r.status_code == 200, r.text
        snap_id = r.json()["snapshot_id"]
    else:
        snap_id = "__baseline__"

    admin_client.patch(
        f"/admin/data/balances/{asset}",
        json={"fields": {"balance": "0.0"}},
    )

    r = admin_client.post("/admin/snapshot/restore",
                          json={"snapshot_id": snap_id})
    assert r.status_code == 200, r.text

    r = admin_client.post("/0/private/Balance")
    assert r.status_code == 200, r.text
    assert r.json()["result"][asset] == pristine_balance


def test_drift_log_records_mutations(admin_client):
    admin_client.post("/admin/drift/log/clear")

    r = admin_client.get("/admin/data/balances")
    asset = r.json()["rows"][0]["asset"]

    admin_client.patch(
        f"/admin/data/balances/{asset}",
        json={"fields": {"balance": "1.234"}},
    )

    r = admin_client.get("/admin/drift/log")
    assert r.status_code == 200
    events = r.json()["events"]
    assert any(e.get("op") == "data.patch" for e in events)


def test_audit_does_not_record_admin_calls(admin_client):
    admin_client.get("/audit/requests/clear")

    admin_client.get("/admin/data/balances")
    admin_client.get("/admin/tables")

    r = admin_client.get("/audit/requests")
    assert r.status_code == 200
    paths = [e["path"] for e in r.json()["requests"]]
    assert not any(p.startswith("/admin") for p in paths), \
        f"admin paths leaked into audit log: {paths}"
