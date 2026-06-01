"""Verbatim port of `_generate_harbor_test_sh` from kensei2.py.

Bash script that Harbor runs inside the sandbox to execute pytest with CTRF
reporting and compute the test reward via test_weights.json.
"""
from __future__ import annotations


_TEST_SH = r"""#!/usr/bin/env bash
set -euo pipefail

mkdir -p /logs/verifier

if ! command -v uv >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

uvx --with pytest==8.4.1 --with pytest-json-ctrf==0.3.5 --with requests \
    pytest --ctrf /logs/verifier/ctrf.json tests/test_outputs.py -rA || true

python3 - <<'PY'
import json
import os

ctrf_path = "/logs/verifier/ctrf.json"
weights_path = "tests/test_weights.json"
reward_path = "/logs/verifier/reward.txt"

ctrf = {}
if os.path.exists(ctrf_path):
    try:
        with open(ctrf_path) as f:
            ctrf = json.load(f)
    except Exception:
        ctrf = {}

results = ctrf.get("results", {}) if isinstance(ctrf, dict) else {}
summary = results.get("summary", {}) if isinstance(results, dict) else {}
tests = results.get("tests", []) if isinstance(results, dict) else []

passed_names = set()
for t in tests:
    if not isinstance(t, dict):
        continue
    status = (t.get("status") or "").lower()
    name = t.get("name") or ""
    if status == "passed" and name:
        passed_names.add(name)

tests_total = int(summary.get("tests", 0) or 0)
tests_passed = int(summary.get("passed", 0) or 0)

weights = {}
if os.path.exists(weights_path):
    try:
        with open(weights_path) as f:
            weights = json.load(f)
    except Exception:
        weights = {}

weights_map = {}
if isinstance(weights, dict):
    weights_map = {str(k): float(v) for k, v in weights.items()
                   if isinstance(v, (int, float))}
elif isinstance(weights, list):
    for item in weights:
        if not isinstance(item, dict):
            continue
        name = item.get("name") or item.get("test")
        w = item.get("weight")
        if name and isinstance(w, (int, float)):
            weights_map[str(name)] = float(w)

pos_total = sum(w for w in weights_map.values() if w > 0)
pos_earned = sum(w for n, w in weights_map.items() if w > 0 and n in passed_names)
neg_penalty = sum(abs(w) for n, w in weights_map.items() if w < 0 and n in passed_names)

if pos_total > 0:
    reward = max(0.0, (pos_earned - neg_penalty) / pos_total)
elif tests_total > 0:
    reward = tests_passed / tests_total
else:
    reward = 0.0

with open(reward_path, "w") as f:
    f.write(f"{reward:.6f}\n")

print(f"reward={reward:.6f} (pos_total={pos_total} pos_earned={pos_earned} neg_penalty={neg_penalty} passed={tests_passed}/{tests_total})")
PY
"""


def generate_harbor_test_sh() -> str:
    """Return the verbatim Harbor `test.sh` bash script."""
    return _TEST_SH
