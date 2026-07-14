#!/usr/bin/env python3
"""Standalone end-to-end checker for Talos inject-format silent injection.

Spins a DEDICATED per-task mock stack for a task (default: LAYLA), enables the
admin plane exactly as eval/run_batch.py does, then runs the real InjectApplier
resolver+patch for every silent mutation in inject/stageN/mutations.json and
reports, per mutation:

    * whether it RESOLVED to a live store row (the bug we just fixed), and
    * whether the target state actually CHANGED (before -> after).

It creates its OWN docker network + container and tears them down at the end, so
it is safe to run while a real harness task is in flight. No agent, no model, no
judge -- $0 and ~30-60s.

Usage:
    python3 script/check_injection.py
    python3 script/check_injection.py input/LAYLA_001_october_grant_crunch
"""
from __future__ import annotations

import subprocess
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import requests  # noqa: E402

from src.utils.mock_stack import (  # noqa: E402
    start_mock_stack, wait_for_ports_healthy, get_published_ports,
    get_network_gateway, stop_mock_stack,
)
from src.utils.docker_utils import discover_services  # noqa: E402
from src.utils.inject_director import InjectScript, InjectApplier  # noqa: E402

ENV_DIR = ROOT / "environment"


def _build_overlays(task_dir: Path) -> dict:
    overlays: dict = {}
    mock_root = task_dir / "mock_data"
    if mock_root.is_dir():
        for api_dir in sorted(mock_root.iterdir()):
            if api_dir.is_dir():
                files = {f.name: str(f.resolve())
                         for f in api_dir.iterdir() if f.is_file()}
                if files:
                    overlays[api_dir.name] = files
    return overlays


def _admin_get(base: str, token: str, suffix: str):
    try:
        r = requests.get(base.rstrip("/") + suffix,
                         headers={"X-Admin-Token": token} if token else {}, timeout=5)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def _target_value(base, token, table, pk, patch_fields):
    """Return the live value(s) of the keys this patch touches, for before/after."""
    row = _admin_get(base, token, f"/admin/data/{table}/{pk}")
    if not isinstance(row, dict):
        return None
    bag = row.get("fields") if isinstance(row.get("fields"), dict) else row
    # patch_fields is either {col: val} or {"fields": {col: val, ...}}
    touched = patch_fields.get("fields") if isinstance(patch_fields.get("fields"), dict) else patch_fields
    return {k: bag.get(k) for k in touched}


def main() -> int:
    task_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "input/LAYLA_001_october_grant_crunch")
    if not (task_dir / "inject").is_dir():
        print(f"[FAIL] {task_dir}/inject not found"); return 2

    overlays = _build_overlays(task_dir)
    services = discover_services(ENV_DIR)
    overlaid_ports = [int(s["port"]) for s in services
                      if s.get("name") in overlays and s.get("port")]
    api_by_port = {int(s["port"]): s["name"] for s in services if s.get("port")}
    if not overlaid_ports:
        print("[FAIL] no overlaid services discovered"); return 2

    net = f"k3net-check-{uuid.uuid4().hex[:8]}"
    container = f"mocks-check-{uuid.uuid4().hex[:6]}"
    token = uuid.uuid4().hex
    print(f"== injection checker ==  task={task_dir.name}  apis={len(overlays)}  ports={overlaid_ports}")
    subprocess.run(["docker", "network", "create", "--internal", net], capture_output=True)
    try:
        gw = get_network_gateway(net) or "127.0.0.1"
        bridge_gw = get_network_gateway("bridge")
        allow = ",".join(dict.fromkeys(g for g in (gw, bridge_gw) if g))
        admin_env = {"MOCK_ADMIN_ENABLED": "1", "MOCK_ADMIN_ALLOWLIST": allow,
                     "MOCK_ADMIN_TOKEN": token}
        print(f"   starting mock stack {container} (admin allowlist={allow}) ...")
        start_mock_stack(container, net, overlays=overlays,
                         admin_env=admin_env, publish_ports=overlaid_ports,
                         enabled_apis=list(overlays.keys()))
        if not wait_for_ports_healthy(container, overlaid_ports, timeout=300.0):
            print("[FAIL] per-task mock stack never became healthy")
            logs = subprocess.run(["docker", "logs", "--tail", "40", container],
                                  capture_output=True, text=True)
            print((logs.stdout or "") + (logs.stderr or ""))
            return 1
        host_ports = get_published_ports(container, overlaid_ports)
        host_api_to_url = {api_by_port[ip]: f"http://127.0.0.1:{hp}"
                           for ip, hp in host_ports.items() if ip in api_by_port}
        if not host_api_to_url:
            print("[FAIL] no host ports resolved (dual-home/publish broken)"); return 1
        print(f"   admin plane reachable for {len(host_api_to_url)} api(s)\n")

        script = InjectScript.load(task_dir / "inject")
        applier = InjectApplier(host_api_to_url, token,
                                Path("/tmp/check_inject_timeline.jsonl"),
                                inject_root=task_dir / "inject")

        total = applied = unresolved = changed = 0
        for stage in script.stages:
            if stage.is_seed or not stage.silent:
                continue
            print(f"-- stage '{stage.name}'  (between T{stage.from_turn}->T{stage.to_turn})")
            for op in stage.silent:
                total += 1
                api = op.get("service") or op.get("api")
                base = host_api_to_url.get(api, "")
                # Explicit admin-op form: dispatch through the real applier, which
                # computes before/after itself (handles bulk + document ops).
                if base and isinstance(op.get("admin"), dict):
                    rec = applier._apply_admin_op(api, op["admin"], op)
                    ok = bool(rec.get("ok"))
                    did_change = bool(rec.get("changed"))
                    applied += 1 if ok else 0
                    changed += 1 if did_change else 0
                    if not ok:
                        unresolved += 1
                    tgt = rec.get("table") or rec.get("document") or ""
                    if rec.get("pk"):
                        tgt = f"{tgt}/{rec['pk']}"
                    if rec.get("matched") is not None:
                        tgt = f"{tgt} (matched={rec['matched']})"
                    flag = "APPLIED" if (ok and did_change) else (
                        "NO-CHANGE" if ok else "UNRESOLVED")
                    print(f"   [{flag}] {op.get('id')}  {api}  {tgt}")
                    print(f"        before={rec.get('before')}  ->  after={rec.get('after')}"
                          f"  ({rec.get('status')})")
                    continue
                resolved = applier._resolve_target(api, op) if base else None
                if not resolved:
                    unresolved += 1
                    print(f"   [UNRESOLVED] {op.get('id')}  {api}  {op.get('path')}")
                    continue
                table, pk, patch_fields = resolved
                before = _target_value(base, token, table, pk, patch_fields)
                result = applier._admin_patch(api, table, pk, patch_fields)
                after = _target_value(base, token, table, pk, patch_fields)
                ok = result.get("ok")
                did_change = before != after
                applied += 1 if ok else 0
                changed += 1 if did_change else 0
                flag = "APPLIED" if (ok and did_change) else ("NO-CHANGE" if ok else "PATCH-FAIL")
                print(f"   [{flag}] {op.get('id')}  {api}  {table}/{pk}")
                print(f"        before={before}  ->  after={after}  (http={result.get('status')})")
            print()

        print(f"== summary ==  silent_ops={total}  resolved={total - unresolved}  "
              f"patched_ok={applied}  state_changed={changed}  unresolved={unresolved}")
        if total and changed == total:
            print("RESULT: PASS — every silent mutation resolved and changed live state.")
            return 0
        print("RESULT: PARTIAL — see per-op lines above (unresolved/no-change are logged, not fatal).")
        return 0
    finally:
        stop_mock_stack(container)
        subprocess.run(["docker", "network", "rm", net], capture_output=True)
        print(f"   cleaned up {container} + {net}")


if __name__ == "__main__":
    raise SystemExit(main())
