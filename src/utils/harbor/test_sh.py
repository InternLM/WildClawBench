"""Verbatim port of `_generate_harbor_test_sh` from kensei2.py.

Bash script that Harbor runs inside the sandbox to execute pytest with CTRF
reporting and compute the test reward via test_weights.json.
"""
from __future__ import annotations


_TEST_SH = r"""#!/usr/bin/env bash
set -euo pipefail

mkdir -p /logs/verifier

# Honor the TEST_DIR contract (verifier env sets /tests); fall back to the
# bundle-relative tests/ layout when the absolute mount is absent so existing
# bundles keep working unchanged.
TEST_DIR="${TEST_DIR:-/tests}"
if [ ! -f "$TEST_DIR/test_outputs.py" ]; then
    TEST_DIR="tests"
fi
export TEST_DIR

if ! command -v uv >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

uvx --with pytest==8.4.1 --with pytest-json-ctrf==0.3.5 --with requests \
    pytest --ctrf /logs/verifier/ctrf.json "$TEST_DIR/test_outputs.py" -rA || true

python3 - <<'PY'
import json
import os

ctrf_path = "/logs/verifier/ctrf.json"
weights_path = os.path.join(os.environ.get("TEST_DIR", "tests"), "test_weights.json")
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

# Build passed-set in three normalized shapes so weight-key lookup matches
# regardless of which form the per-task test_weights.json uses:
#   - full CTRF name      (e.g. "tests/test_outputs.py::TestFoo::test_bar")
#   - class-qualified     (e.g. "TestFoo::test_bar")
#   - bare test name      (e.g. "test_bar")
# This single normalisation fixes BOTH:
#   A.1 (CTRF-FQN-vs-bare-key) — CTRF emits "tests/test_outputs.py::Class::test_x"
#       but test_weights.json frequently holds bare "test_x"; the prior code's
#       `n in passed_names` never matched, so pos_earned stayed 0 even when
#       every test passed (root cause behind 27/50 vendor GRADER_BROKEN tasks).
#   A.2 (bare-name collisions across multi-service classes) — when one bare
#       name (e.g. "test_no_post_requests_made") appears in 4 service classes,
#       test_weights.json can only hold one entry per bare key. A bare weight
#       key now resolves to a class-aware multiset: it counts as PASSED iff
#       at least one class's variant passed (treats the bare key as "any
#       service passed this check"). Class-qualified weight keys remain
#       precise. Tasks like chen-amazon-sales, sandeep-marathon-nutrition,
#       megan-bbq-recap, alden-boat-closeout, angela-nanite-deck depend on
#       this multiset semantics.
passed_full = set()
passed_class_qual = set()  # "TestFoo::test_bar"
passed_bare = set()        # "test_bar" (collapses across classes)
for t in tests:
    if not isinstance(t, dict):
        continue
    status = (t.get("status") or "").lower()
    name = t.get("name") or ""
    if status != "passed" or not name:
        continue
    passed_full.add(name)
    parts = name.split("::")
    if len(parts) >= 2:
        passed_bare.add(parts[-1])
    if len(parts) >= 3:
        passed_class_qual.add("::".join(parts[-2:]))
    elif len(parts) == 2:
        # No class wrapper (module-level test) — still record bare; the
        # class-qualified slot stays empty so only bare/full-name lookups
        # can resolve it.
        passed_class_qual.add(name.split("::")[-1])

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

def _key_passed(key):
    # Resolve a test_weights.json key against the passed-name shapes.
    # A class-qualified key MUST match precisely — falling back to the
    # bare-multiset would let any other class's pass spuriously satisfy a
    # different class's weight (verified by the class-qualified-precision
    # smoke case). Only a bare key (no "::") gets the A.2 multiset semantics.
    if key in passed_full:
        return True
    if "::" in key:
        return key in passed_class_qual
    return key in passed_bare

pos_total = sum(w for w in weights_map.values() if w > 0)
pos_earned = sum(w for n, w in weights_map.items() if w > 0 and _key_passed(n))
neg_penalty = sum(abs(w) for n, w in weights_map.items() if w < 0 and _key_passed(n))

if pos_total > 0:
    reward = (pos_earned - neg_penalty) / pos_total
elif tests_total > 0:
    reward = tests_passed / tests_total
else:
    reward = 0.0

with open(reward_path, "w") as f:
    f.write(f"{reward:.6f}\n")

if isinstance(ctrf, dict) and isinstance(results, dict) and isinstance(summary, dict):
    summary["overall_score"] = round(reward, 4)
    summary["weighted_percentage"] = round(reward * 100.0, 2)
    results["summary"] = summary
    ctrf["results"] = results
    with open(ctrf_path, "w") as f:
        json.dump(ctrf, f, indent=2, ensure_ascii=False)

print(f"reward={reward:.6f} (pos_total={pos_total} pos_earned={pos_earned} neg_penalty={neg_penalty} passed={tests_passed}/{tests_total})")
PY
"""


def generate_harbor_test_sh() -> str:
    """Return the verbatim Harbor `test.sh` bash script."""
    return _TEST_SH
