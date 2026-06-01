from __future__ import annotations

from pathlib import Path

import pytest

from ._helpers import substitute_path_params


def test_imports_cleanly(app):
    assert app is not None
    assert hasattr(app, "routes")
    assert len(app.routes) > 0


def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200, f"/health returned {resp.status_code}"
    body = resp.json()
    assert body.get("status") == "ok"


def test_audit_summary_endpoint(client):
    resp = client.get("/audit/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert "total_requests" in body
    assert "endpoints" in body


def test_audit_requests_endpoint(client):
    resp = client.get("/audit/requests")
    assert resp.status_code == 200


def test_no_route_returns_5xx(client, routes, id_pool):
    crashed: list[tuple[str, str, int, str]] = []
    for method, path in routes:
        concrete = substitute_path_params(path, id_pool)
        try:
            if method == "GET":
                resp = client.get(concrete)
            elif method == "POST":
                resp = client.post(concrete, json={})
            elif method == "PUT":
                resp = client.put(concrete, json={})
            elif method == "PATCH":
                resp = client.patch(concrete, json={})
            elif method == "DELETE":
                resp = client.delete(concrete)
            else:
                continue
        except Exception as e:
            crashed.append((method, path, -1, f"client exception: {e}"))
            continue
        if resp.status_code >= 500:
            try:
                body = resp.text[:200]
            except Exception:
                body = "<no body>"
            crashed.append((method, path, resp.status_code, body))

    assert not crashed, (
        "Mock handler raised an unhandled exception (5xx) on "
        f"{len(crashed)} route(s):\n"
        + "\n".join(f"  {m} {p} -> {s}: {b}" for m, p, s, b in crashed)
    )


def test_service_toml_required_keys(service_cfg):
    for key in ("name", "port", "env_var_name", "healthcheck_path"):
        assert key in service_cfg, f"service.toml missing {key!r}"
    assert isinstance(service_cfg["port"], int)
    assert 1024 <= service_cfg["port"] <= 65535
    assert service_cfg["healthcheck_path"].startswith("/")
