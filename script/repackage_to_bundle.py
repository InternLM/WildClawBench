#!/usr/bin/env python3
"""Standalone repackager: raw run-output  ->  published "bundle" structure.

This script is intentionally ISOLATED from the eval pipeline. It only reads an
existing run-output tree and writes a NEW bundle tree; it never touches the
pipeline code, never runs Docker, never calls an LLM. Run it whenever you want
to publish a finished run.

WHAT IT DOES
------------
Given our raw layout (produced by eval/run_batch.py):

    <source-root>/<task_id>/
        prompt.txt, rubric.json, data/ ...
        trajectories/<harness>/            (e.g. "claude")
            pass_summary.json
            run_N/
                output.json, score.json, usage.json, chat.jsonl, ...
                task_output/
                    artifacts/<written files>        (+ _tmp/ scratch)
                    logs/verifier/{ctrf.json,reward.txt,test_weights.json}

it emits the published bundle layout (like the amanda_webb_01 reference):

    <dest-root>/<bundle_name>/
        prompt.txt, rubric.json, data/ ...           (skeleton copied as-is)
        ground-truth.md                              (input golden_steer_flow.md,
                                                       sliced to Focal Event +
                                                       Canonical Solve Path +
                                                       Value Lock sections)
        trajectories/<Pretty Model>/                 (e.g. "Claude Opus 4.7")
            pass_summary.json                         (REBUILT schema)
            run_N/
                output.json                           (copied as-is)
                logs/verifier/                        (raw: ctrf.json,
                                                       test_weights.json,
                                                       reward.txt, siblings)
                report.json                           (BUILT from ctrf+score)
                output_media/<rendered files>         (artifacts minus _tmp/)

MATCHING (requirements 2 & 3)
-----------------------------
Source task dirs and the published bundle dirs are NOT named identically
(e.g. "ben_cox_8fc24d4b-..." vs a desired "ben_cox_01", or "amanda_webb_01").
We match on the PERSONA CORE NAME by normalizing: strip emoji / non-alphanumeric,
lowercase, drop any trailing uuid / numeric / hash suffix tokens, collapse
separators. So "ben cox", "ben_cox_8fc24d4b-..." and "ben_cox_01" all reduce to
the key "ben cox". The emoji-prefixed dir ("\U0001f7e2sheila_stokes_...") is handled.

The litellm-proxy difference between trees is IGNORED entirely (requirement 4):
we never read or write data/environment/litellm-proxy.

SELECTING WHAT TO CONVERT
-------------------------
  --persona "ben cox"     convert only the task whose core name matches "ben cox"
  --all                   convert every task dir under <source-root>
You must pass exactly one of --persona / --all.

DESIGN CHOICES (documented, since some target fields are absent in our data)
---------------------------------------------------------------------------
* report.json.final_reward            <- score.json.combined_reward
  (most faithful overall reward; the reference bundle's final_reward happens to
  equal its rubric percentage only because its test score was 100%.)
* report.json.test_weights_percentage <- ctrf.json.results.summary.weighted_percentage
  (falls back to reward.txt * 100 when ctrf is missing)
* report.json.rubric_weights_percentage <- score.json.rubric_weights_percentage
* rubric[].number          <- "R" + (score.json.criteria[].id + 1)
* rubric[].score           <- int(criteria[].weight)
* rubric[].is_positive     <- criteria[].is_positive
* rubric[].passed          <- criteria[].passed   (for negative items, passed==True
                              means the agent correctly AVOIDED the bad behavior,
                              matching the reference semantics)
* rubric[].justification   <- single-judge criteria[].rationale, or, on a council
                              score.json, the first non-empty criteria[].rationales_by_judge
                              entry; emitted ONLY on failed items (empty string if none)
* rubric[].type / importance / evaluation_target are NOT in our score.json.
    - importance is DERIVED: abs(weight) >= 5 -> "critically_important" else "important"
    - type and evaluation_target are emitted as "" (unknown) unless --infer-rubric-meta
      is passed, in which case light heuristics fill them (see _infer_meta).
* pytest test name           <- bare test name (last "::" segment of the ctrf
                              name; class/module/file qualifiers are stripped)
* pytest test weight         <- test_weights.json[method]  (default 1 if absent)
* include_multimodal         <- True if rubric/task mentions image/document OR any
                                input_files mime is image/* (see _detect_multimodal)
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path
from typing import Any


# Extend as new harnesses/models are published. Default direct-Anthropic path
# runs Opus 4.7, so "claude" -> "Claude Opus 4.7".
MODEL_LABELS: dict[str, str] = {
    "claude": "Claude Opus 4.7",
    "claudecode": "Claude Opus 4.7",
    "openclaw": "Claude Opus 4.7",
    "gpt": "GPT 5.5",
    "codex": "GPT 5.5",
    "hermes": "Hermes",
    "hermesagent": "Hermes",
}

# Scratch subdir inside artifacts/ that must never be published.
ARTIFACTS_SCRATCH_DIRNAME = "_tmp"

# The run-output tree strips the persona/ and staged input files from
# data/environment/. The published bundle (amanda_webb reference) keeps them, so
# we re-source them from the ORIGINAL task input dir (default root: "input").
# Where staged inputs live inside the bundle's environment dir.
ARTIFACTS_INPUTS_SUBPATH = ("artifacts", "inputs", "files")

# Grader "golden steer flow" re-sourced from the original input task dir and
# published into the bundle root under a stable, consumer-facing name. Renamed
# (not relocated) so downstream tooling can rely on "ground-truth.md". Contents
# are NOT byte-copied: only three target sections are extracted (Focal Event,
# Canonical Solve Path, Value Lock) so the published bundle does not leak the
# full author-side flow doc. See extract_ground_truth_sections() below.
GOLDEN_STEER_FILENAME = "golden_steer_flow.md"
GROUND_TRUTH_FILENAME = "ground-truth.md"

# Source-file lookup order for the slice. Upstream authoring tools have
# emitted the same content under three different filenames over time, so we
# accept any of them; first match wins. Order is the resolution priority:
# GTFA.md (newest convention) -> golden_steer_flow.md (legacy) ->
# ground-truth.md (already-sliced fallback). Note that ground-truth.md as
# input is idempotent under extract_ground_truth_sections(): re-extracting
# the three target sections from a file that already only contains them is a
# no-op other than re-emitting them in canonical order.
GROUND_TRUTH_SOURCE_CANDIDATES: tuple[str, ...] = (
    "GTFA.md",
    "golden_steer_flow.md",
    "ground-truth.md",
)

# Heading aliases for the published ground-truth slice. Each tuple is a set of
# case-insensitive substrings; a heading matches the section if its normalized
# text contains ANY alias. Matching is on the heading TEXT only (decorations,
# section-number prefixes, trailing words like "and Scope" are stripped first
# in _normalize_heading_text). Order here is the order sections are emitted.
GROUND_TRUTH_SECTION_ALIASES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Focal Event", ("focal event",)),
    ("Canonical Solve Path", ("canonical solve path",)),
    # "Value Lock" covers titlecase, ALLCAPS, and underscore/hyphen variants
    # because _normalize_heading_text() collapses [_\-\s]+ to single spaces and
    # lowercases. So "VALUE_LOCK", "Value-Lock", "Value Lock" all hit.
    ("Value Lock", ("value lock",)),
)

# Section-prefix patterns we strip from heading text before alias matching so
# "Section 1: Focal Event and Scope" -> "focal event and scope" -> matches.
# Each pattern is anchored to the start of the (already lowercased) heading.
#
# NOTE on strategy: prefix-stripping is DEFENSIVE, not load-bearing. Alias
# matching is substring-based (`alias in normalized`), so even if a prefix
# slips through ("Chapter II — Focal Event" -> "chapter ii focal event"),
# the substring "focal event" still matches. The prefix regex exists to keep
# normalized output tidy and to absorb common author conventions; widening
# it never breaks correctness, only improves matched headings' cleanliness.
#
# Keywords covered (case-insensitive after lower()):
#   section, sec, s, part, pt, chapter, ch, chap, step, phase, appendix
# Numbering covered: ASCII digits 0-9 (with optional multi-level like 2.1),
#   single ASCII letter (Appendix A), roman numerals i..mmmm (lowercased).
# Separators between number and title: `:` `.` `-` `)` `]` em-dash `—`
#   en-dash `–`, or whitespace alone.
# Also covers identifier-style prefixes used by upstream authoring tools, e.g.
# "GS-4 Title", "GS-4: Title", "WCB-12 - Title" (1-6 ASCII letters, optional
# dash/space, digits, optional separator). These appear in real golden_steer
# files as cross-reference IDs and must NOT survive into the slice key.
_HEADING_PREFIX_RE = re.compile(
    r"""^(?:
        # keyword + (number|letter|roman) + optional separator
        (?:section|sec\.?|s\.|part|pt\.?|chapter|chap\.?|ch\.?|step|phase|appendix)
        \s*
        (?:\d+(?:\.\d+)*|[ivxlcdm]+|[a-z])?      # number / multi-level / roman / letter
        \s*
        [:.\-)\]\u2013\u2014]?                   # separator (or none)
        \s*
        |
        # identifier-style: 1-6 letters + optional dash/space + digits, e.g.
        # "gs-4", "gs 4", "wcb-12". Trailing separator (":", "-", em/en dash,
        # ".", ")", "]") optional.
        [a-z]{1,6}[\s\-\u2013\u2014]?\d+(?:\.\d+)*\s*[:.\-)\]\u2013\u2014]?\s*
        |
        # bare numeric prefix: "1." "1)" "(1)" "[1]" "1-" "1:"
        [(\[]?\s*\d+(?:\.\d+)*\s*[)\]]?\s*[:.\-)\u2013\u2014]?\s*
    )""",
    re.VERBOSE,
)

# ATX heading: 1-6 leading '#', optional space, capture text, optional trailing
# '#'s. Allows up to 3 spaces of indentation per CommonMark.
_ATX_HEADING_RE = re.compile(r"^[ ]{0,3}(#{1,6})\s*(.+?)\s*#*\s*$")

# Setext underlines: '=' (h1) or '-' (h2), at least 1 char, possibly indented.
_SETEXT_H1_RE = re.compile(r"^[ ]{0,3}=+\s*$")
_SETEXT_H2_RE = re.compile(r"^[ ]{0,3}-+\s*$")

# Harness-runtime files re-sourced from the harness's own `environment/` dir
# into every published bundle's `data/environment/`. These power the runtime
# admin plane / mutable store / instrumentation that bundle consumers replay
# against — keeping them in lock-step with the harness avoids drift. The path
# is derived from this script's own location (one level up = harness root) so
# the rule is portable across machines / checkout paths.
HARNESS_ENV_FILES: tuple[str, ...] = (
    "tracking_middleware.py",
    "admin_plane.py",
    "_mutable_store.py",
)
HARNESS_ROOT = Path(__file__).resolve().parent.parent
HARNESS_ENV_DIR = HARNESS_ROOT / "environment"


# ----------------------------------------------------------------------------
# Test runners + solver scaffolding (data/tests/, data/solution/)
# ----------------------------------------------------------------------------
# These four files are part of the published bundle contract and were emitted
# by the legacy Harbor path (src/utils/harbor/bundle.py + solve_sh.py + test_sh.py).
# After the b1 refactor routed auto-bundle through this standalone script the
# emissions were silently lost (see docs/reps-failure-diagnosis.md ancestry).
#
# We INLINE-PORT the Harbor generators rather than `from src.utils.harbor import`
# because this module is intentionally standalone + stdlib-only (script/AGENTS.md
# convergence invariant + zero-dep posture so deliver.sh and run.sh can call it
# without dragging the eval venv along).
#
# Sources (all confirmed at TASK ROOT, NOT under data/tests/):
#   input/<task>/test_outputs.py    -> bundle/data/tests/test_outputs.py
#   input/<task>/test_weights.json  -> bundle/data/tests/test_weights.json
#   <generated>                     -> bundle/data/tests/test.sh
#   <generated from env_vars>       -> bundle/data/solution/solve.sh
#
# `test.sh` is 100% static (port of src/utils/harbor/test_sh.py::_TEST_SH).
# `solve.sh` is parameterized by env_vars discovered from bundle/data/environment/
# (each <api>/service.toml -> env_var_name -> http://<name>:<port>). This mirrors
# what src/utils/mock_stack.py::start_mock_stack exports to the agent container,
# so the published solve.sh references the same env var names the agent saw.
TEST_OUTPUTS_FILENAME = "test_outputs.py"
TEST_OUTPUTS_FILENAME_LEGACY = "test_output.py"
TEST_WEIGHTS_FILENAME = "test_weights.json"
TEST_SH_FILENAME = "test.sh"
SOLVE_SH_FILENAME = "solve.sh"
TESTS_SUBDIR = "tests"
SOLUTION_SUBDIR = "solution"


def _resolve_test_outputs_source(input_task_dir: Path) -> Path | None:
    for name in (TEST_OUTPUTS_FILENAME, TEST_OUTPUTS_FILENAME_LEGACY):
        cand = input_task_dir / name
        if cand.is_file():
            return cand
    return None
SERVICE_TOML_FILENAME = "service.toml"

# Verbatim port of src/utils/harbor/test_sh.py::_TEST_SH (157-line static bash
# script). Touch in lock-step with that file; if it ever needs to diverge,
# document why in script/AGENTS.md.
_TEST_SH: str = r"""#!/usr/bin/env bash
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


# Tokens that look like a uuid / hex hash / pure-number suffix get dropped so the
# persona "core" survives. e.g. ben_cox_8fc24d4b-dd01-... -> "ben cox".
_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
_HEX_RE = re.compile(r"^[0-9a-f]{6,}$", re.I)
_NUM_RE = re.compile(r"^\d+$")


def _strip_emoji(text: str) -> str:
    """Drop emoji / symbol / non-ascii pictographs, keep letters/digits/separators."""
    out = []
    for ch in text:
        cat = unicodedata.category(ch)
        # So=other symbol (most emoji), Sk=modifier symbol, Cs=surrogate, Co=private.
        if cat in {"So", "Sk", "Cs", "Co"}:
            continue
        out.append(ch)
    return "".join(out)


def persona_core(name: str) -> str:
    """Reduce any folder/persona label to its comparable core key.

    "\U0001f7e2sheila_stokes_c74d93d8-..."  -> "sheila stokes"
    "ben_cox_8fc24d4b-dd01-44db-95b5-..."   -> "ben cox"
    "amanda_webb_01"                          -> "amanda webb"
    "alden-croft"                             -> "alden croft"
    """
    name = _strip_emoji(name)
    name = name.lower()
    # Split on separators and whitespace.
    tokens = re.split(r"[\s\-_]+", name)
    kept: list[str] = []
    for tok in tokens:
        if not tok:
            continue
        # Drop uuid/hex/numeric suffix tokens (they are run/instance ids, not names).
        if _UUID_RE.match(tok) or _HEX_RE.match(tok) or _NUM_RE.match(tok):
            continue
        # Drop leftover non-alphanumeric debris.
        tok = re.sub(r"[^a-z0-9]+", "", tok)
        if tok:
            kept.append(tok)
    return " ".join(kept).strip()


def _load_json(path: Path) -> Any | None:
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def _pretty_model(harness_dirname: str) -> str:
    key = harness_dirname.strip().lower()
    return MODEL_LABELS.get(key, harness_dirname)


def _strip_inline_decoration(text: str) -> str:
    """Strip leading/trailing **bold**, *italic*, __bold__, _italic_, backticks."""
    prev = None
    cur = text.strip()
    while cur != prev:
        prev = cur
        for n in (3, 2, 1):
            for ch in ("*", "_", "`"):
                wrap = ch * n
                if len(cur) >= 2 * n and cur.startswith(wrap) and cur.endswith(wrap):
                    cur = cur[n:-n].strip()
                    break
    return cur


def _normalize_heading_text(raw: str) -> str:
    """Lower-case, strip decorations + section prefixes, collapse to alphanum+space.

    The final collapse step replaces any run of NON-alphanumeric characters
    with a single space. This is intentionally broad so the same alias hits
    every plausible authoring style:
      - separator variants: ``Value-Lock`` ``Value_Lock`` ``Value/Lock``
        ``Value.Lock`` ``Value Lock`` ``Value\u2014Lock`` (em dash)
        ``Value\u2013Lock`` (en dash) ``Value\u00a0Lock`` (NBSP)
      - leftover decoration noise: ``**focal** event`` -> ``focal event``
      - HTML/anchor trailers: ``focal event {#anchor}`` -> ``focal event anchor``
      - emoji / pictographs: ``\U0001F7E2 focal event`` -> ``focal event``
    Alias matching is substring-based on this normalized form, so canonical
    aliases stay short and authors get tolerance "for free".
    """
    text = _strip_inline_decoration(raw).lower()
    text = _HEADING_PREFIX_RE.sub("", text).strip()
    # Collapse every non-alphanumeric run (Unicode dashes, slashes, periods,
    # NBSP, emoji, residual punctuation, leftover decoration markers, etc.)
    # to a single ASCII space. Keep digits in case future aliases use them.
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return text.strip()


def _iter_headings(lines: list[str]):
    """Yield (line_index, level, normalized_text) for every heading in `lines`.

    Handles ATX (`#`..`######`) and setext (text underlined with `===`/`---`).
    Skips fenced code blocks so a `# comment` inside a ``` block is not parsed.
    """
    in_fence = False
    fence_char = ""
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            ch = stripped[0]
            if not in_fence:
                in_fence = True
                fence_char = ch
            elif ch == fence_char:
                in_fence = False
                fence_char = ""
            i += 1
            continue
        if in_fence:
            i += 1
            continue
        m = _ATX_HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            yield i, level, _normalize_heading_text(m.group(2))
            i += 1
            continue
        if i + 1 < n and line.strip():
            nxt = lines[i + 1]
            if _SETEXT_H1_RE.match(nxt):
                yield i, 1, _normalize_heading_text(line)
                i += 2
                continue
            if _SETEXT_H2_RE.match(nxt):
                yield i, 2, _normalize_heading_text(line)
                i += 2
                continue
        i += 1


def _heading_matches(normalized: str, aliases: tuple[str, ...]) -> bool:
    return any(alias in normalized for alias in aliases)


def _heading_span_end(line_idx: int, level: int, lines: list[str]) -> int:
    """Find the line AFTER the body of a heading whose underline/hash sits at line_idx.

    Body ends at the next heading of equal-or-shallower level, or EOF. Thematic
    breaks (`---`) inside the body are KEPT (they are decorative separators in
    the source flow doc); the consumer can strip them if undesired.
    """
    headings = list(_iter_headings(lines))
    for hi, hlevel, _ in headings:
        if hi > line_idx and hlevel <= level:
            return hi
    return len(lines)


def extract_ground_truth_sections(text: str) -> str:
    """Return only the target sections (Focal Event / Canonical Solve Path /
    Value Lock) from a `golden_steer_flow.md` body, in the order declared by
    GROUND_TRUTH_SECTION_ALIASES. Each emitted section keeps its original
    heading line and body verbatim. If a target section is missing the
    function silently skips it. The output ends with a single trailing
    newline; sections are separated by one blank line.
    """
    if not text:
        return ""
    lines = text.splitlines()
    headings = list(_iter_headings(lines))

    chunks: list[str] = []
    seen_targets: set[str] = set()
    for hi, level, norm in headings:
        for canonical, aliases in GROUND_TRUTH_SECTION_ALIASES:
            if canonical in seen_targets:
                continue
            if not _heading_matches(norm, aliases):
                continue
            end = _heading_span_end(hi, level, lines)
            body_lines = lines[hi:end]
            while body_lines and not body_lines[-1].strip():
                body_lines.pop()
            if body_lines:
                chunks.append("\n".join(body_lines))
            seen_targets.add(canonical)
            break

    ordered: list[str] = []
    for canonical, _ in GROUND_TRUTH_SECTION_ALIASES:
        for chunk in chunks:
            first = chunk.splitlines()[0] if chunk else ""
            if _heading_matches(_normalize_heading_text(first), (canonical.lower(),)):
                ordered.append(chunk)
                break

    if not ordered:
        return ""
    return "\n\n".join(ordered) + "\n"


def _method_of(test_name: str) -> str:
    """ctrf name is 'Class::method'; weights key is bare 'method'."""
    return test_name.split("::")[-1]


def _build_pytest_block(verifier_dir: Path) -> dict[str, Any]:
    ctrf = _load_json(verifier_dir / "ctrf.json") or {}
    weights = _load_json(verifier_dir / "test_weights.json") or {}
    results = ctrf.get("results", {}) if isinstance(ctrf, dict) else {}
    summary = results.get("summary", {}) if isinstance(results, dict) else {}
    raw_tests = results.get("tests", []) if isinstance(results, dict) else []

    # Weights keys may be bare ("test_x") or qualified ("TestFoo::test_x",
    # "tests/test_outputs.py::TestFoo::test_x"); fold them to bare names so
    # they resolve against the bare ctrf test names.
    bare_weights = {_method_of(k): v for k, v in weights.items()}

    tests: list[dict[str, Any]] = []
    for t in raw_tests:
        name = t.get("name", "")
        method = _method_of(name)
        weight = weights.get(name, bare_weights.get(method, 1))
        tests.append(
            {
                "name": method,
                "weight": int(weight),
                "passed": t.get("status") == "passed",
            }
        )

    # reward.txt fallback for percentage if ctrf summary missing.
    reward_txt = None
    rtxt = verifier_dir / "reward.txt"
    if rtxt.exists():
        try:
            reward_txt = float(rtxt.read_text().strip())
        except ValueError:
            reward_txt = None

    passed = int(summary.get("passed", sum(1 for t in tests if t["passed"])))
    failed = int(summary.get("failed", sum(1 for t in tests if not t["passed"])))
    reward = summary.get("overall_score")
    if reward is None:
        reward = reward_txt if reward_txt is not None else 0.0

    return {
        "passed": passed,
        "failed": failed,
        "exit_code": 0 if failed == 0 else 1,
        "reward": float(reward),
        "tests": tests,
    }, summary, reward_txt


def _infer_meta(criterion: str, is_positive: bool) -> tuple[str, str]:
    """Light heuristic for (type, evaluation_target) when --infer-rubric-meta set.

    Kept conservative: only obvious keyword hits, else ("", "").
    """
    c = criterion.lower()
    typ = ""
    if any(w in c for w in ("must not", "should not", "no ", "without", "avoid", "distractor")):
        typ = "safety & boundaries" if not is_positive else "instruction following"
    elif any(w in c for w in ("state", "writes", "records", "generates", "file", ".docx", ".pdf")):
        typ = "task completion"
    elif any(w in c for w in ("hallucinat", "factual", "sourced", "references", "identifies")):
        typ = "factuality and hallucination"
    elif any(w in c for w in ("tool", "api", "endpoint", "queried", "fetch")):
        typ = "tool use"

    target = ""
    if any(w in c for w in ("file", "writes", "records", "generates", ".docx", ".pdf", "inside")):
        target = "state_change"
    elif any(w in c for w in ("tool", "image-processing", "trajectory", "uses an")):
        target = "trajectory"
    elif any(w in c for w in ("response states", "response presents", "final", "answer")):
        target = "final_answer"
    return typ, target


def _pick_rationale(c: dict[str, Any]) -> str:
    rationale = c.get("rationale")
    if isinstance(rationale, str) and rationale:
        return rationale
    by_judge = c.get("rationales_by_judge")
    if isinstance(by_judge, list):
        for r in by_judge:
            if isinstance(r, str) and r:
                return r
    return ""


def _build_rubric_block(score: dict[str, Any], infer_meta: bool) -> list[dict[str, Any]]:
    rubric: list[dict[str, Any]] = []
    for c in score.get("criteria", []):
        weight = c.get("weight", 0)
        is_positive = bool(c.get("is_positive", weight >= 0))
        criterion = c.get("criterion", "")
        importance = "critically_important" if abs(float(weight)) >= 5 else "important"
        typ, target = _infer_meta(criterion, is_positive) if infer_meta else ("", "")
        passed = bool(c.get("passed", False))
        item: dict[str, Any] = {
            "number": f"R{int(c.get('id', 0)) + 1}",
            "criterion": criterion,
            "type": typ,
            "evaluation_target": target,
            "importance": importance,
            "score": int(weight),
            "is_positive": is_positive,
            "passed": passed,
        }
        if not passed:
            item["justification"] = _pick_rationale(c)
        rubric.append(item)
    return rubric


def _detect_multimodal(task_dir: Path, output_json: dict[str, Any] | None) -> bool:
    # task.yaml / task.toml modalities
    for fname in ("task.yaml", "data/task.toml", "task.toml"):
        p = task_dir / fname
        if p.exists():
            txt = p.read_text(encoding="utf-8", errors="ignore").lower()
            if "image" in txt or "document" in txt or "multimodal" in txt:
                return True
    # input_files mimes in output.json
    if isinstance(output_json, dict):
        traj = output_json.get("trajectory", {})
        files = output_json.get("input_files") or traj.get("input_files") or []
        for f in files:
            mime = (f.get("mime") or f.get("mime_type") or "") if isinstance(f, dict) else ""
            if isinstance(mime, str) and mime.startswith("image/"):
                return True
    return False


def build_report(
    run_dir: Path,
    task_dir: Path,
    pretty_model: str,
    run_index: int,
    infer_meta: bool,
) -> dict[str, Any]:
    verifier = run_dir / "task_output" / "logs" / "verifier"
    score = _load_json(run_dir / "score.json") or {}
    output_json = _load_json(run_dir / "output.json")

    pytest_block, ctrf_summary, reward_txt = _build_pytest_block(verifier)
    rubric_block = _build_rubric_block(score, infer_meta)

    test_pct = ctrf_summary.get("weighted_percentage")
    if test_pct is None:
        test_pct = (reward_txt * 100.0) if reward_txt is not None else 0.0
    rubric_pct = score.get("rubric_weights_percentage", 0.0)
    final_reward = score.get("combined_reward")
    if final_reward is None:
        final_reward = score.get("rubric_based_reward", 0.0)

    return {
        "model": pretty_model,
        "run_index": run_index,
        "include_multimodal": _detect_multimodal(task_dir, output_json),
        "pytest": pytest_block,
        "rubric": rubric_block,
        "final_reward": round(float(final_reward), 4),
        "test_weights_percentage": round(float(test_pct), 2),
        "rubric_weights_percentage": round(float(rubric_pct), 2),
    }


def _stage_verifier_test_sources(
    input_task_dir: Path | None,
    dest_verifier: Path,
    verbose: bool,
) -> tuple[bool, bool, bool]:
    """Mirror `test.sh` + `test_outputs.py` + `test_weights.json` into
    each per-rep `logs/verifier/` next to the run outputs (ctrf, reward,
    test_output.log, test_function_outputs).

    Symmetrical with the host-side mirror in
    `eval/run_batch.py` (post-execution write next to `test_output.log`).
    The bundle's `copy_verifier_logs()` will already inherit these three
    files when present in the source `output/<backend>/<task>/.../logs/verifier/`;
    this helper is the BACKFILL path for two cases:
      (1) older output trees that pre-date the run_batch.py mirror, and
      (2) standalone `repackage_to_bundle.py` runs that import-by-bash.
    On a fresh run the writes here are no-ops (target already populated
    by `copy_verifier_logs`); idempotent.

    Source resolution:
      - `test.sh`           -> re-emit via `_generate_test_sh()` (stdlib-only)
      - `test_outputs.py`   -> `input_task_dir/test_outputs.py` (task ROOT, NOT data/tests/)
      - `test_weights.json` -> `input_task_dir/test_weights.json`

    When `input_task_dir` is None we still emit `test.sh` because it has
    zero input-side dependency.
    """
    dest_verifier.mkdir(parents=True, exist_ok=True)
    wrote_test_sh = False
    wrote_outputs = False
    wrote_weights = False
    test_sh_path = dest_verifier / TEST_SH_FILENAME
    if not test_sh_path.exists():
        test_sh_path.write_text(_generate_test_sh(), encoding="utf-8")
        wrote_test_sh = True
    if input_task_dir is not None:
        src_outputs = _resolve_test_outputs_source(input_task_dir)
        dst_outputs = dest_verifier / TEST_OUTPUTS_FILENAME
        if src_outputs is not None and not dst_outputs.exists():
            shutil.copy2(src_outputs, dst_outputs)
            wrote_outputs = True
        src_weights = input_task_dir / TEST_WEIGHTS_FILENAME
        dst_weights = dest_verifier / TEST_WEIGHTS_FILENAME
        if src_weights.is_file() and not dst_weights.exists():
            shutil.copy2(src_weights, dst_weights)
            wrote_weights = True
    if verbose:
        print(
            f"      logs/verifier mirror: test.sh={wrote_test_sh} "
            f"test_outputs.py={wrote_outputs} test_weights.json={wrote_weights}"
        )
    return wrote_test_sh, wrote_outputs, wrote_weights


# Harness-injected wall-clock prefix on subagent context messages, e.g.
# `[Thu 2026-06-25 14:38 UTC] `. Stripped for published-trajectory hygiene.
_CLOCKSTAMP_RE = re.compile(
    r"\[(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun) \d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC\] ?")


def _strip_clockstamps_in_dir(root: Path) -> int:
    """Remove the harness-injected ``[Day YYYY-MM-DD HH:MM UTC]`` wall-clock
    prefix from subagent trajectory JSON (published-trajectory hygiene).

    Operates on raw file text so JSON formatting is preserved verbatim and only
    the stamp token is removed; legitimate clock references inside deliverable
    prose (e.g. a cron time "12:00 UTC") never match the bracketed pattern.
    Returns the number of files modified."""
    n = 0
    if not root.is_dir():
        return 0
    for jf in root.rglob("*.json"):
        text = jf.read_text(encoding="utf-8")
        cleaned = _CLOCKSTAMP_RE.sub("", text)
        if cleaned != text:
            jf.write_text(cleaned, encoding="utf-8")
            n += 1
    return n


def copy_subagent_artifacts(run_dir: Path, dest_run: Path) -> int:
    """Copy native multi-agent artifacts into the bundle run dir.

    subagents/ holds the child trajectories written by attach_native_subagents
    (always created so the multi-agent validator passes; empty for single-agent
    runs). spawn_tree/ (parent_spawn_tree.txt) is carried through when present.
    """
    dest_sub = dest_run / "subagents"
    dest_sub.mkdir(parents=True, exist_ok=True)
    count = 0
    src_sub = run_dir / "subagents"
    if src_sub.is_dir():
        shutil.copytree(
            src_sub, dest_sub,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(".DS_Store"),
        )
        count += sum(1 for _ in dest_sub.rglob("*") if _.is_file())
        # Strip harness-injected wall-clock prefixes from the published
        # subagent trajectories (hygiene); leaves all else byte-identical.
        _strip_clockstamps_in_dir(dest_sub)
    src_tree = run_dir / "spawn_tree"
    if src_tree.is_dir():
        shutil.copytree(
            src_tree, dest_run / "spawn_tree",
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(".DS_Store"),
        )
        count += sum(1 for _ in (dest_run / "spawn_tree").rglob("*") if _.is_file())
    return count


def copy_verifier_logs(run_dir: Path, dest_run: Path) -> int:
    """Copy task_output/logs/verifier/* into the bundle at run_N/logs/verifier/*.

    Preserves the raw pytest CTRF, test_weights, reward.txt and any sibling
    artifacts the harness emits there. report.json carries a normalized view
    derived from these inputs, but downstream tooling (pytest-replay, third-
    party grading, audit) needs the raw inputs too. Mirrors copy_output_media:
    same scratch-skip + .DS_Store guard pattern.
    """
    src = run_dir / "task_output" / "logs" / "verifier"
    dest = dest_run / "logs" / "verifier"
    if not src.is_dir():
        return 0
    dest.mkdir(parents=True, exist_ok=True)
    count = 0
    for item in src.iterdir():
        if item.name == ".DS_Store":
            continue
        target = dest / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
            count += sum(1 for _ in target.rglob("*") if _.is_file())
        else:
            shutil.copy2(item, target)
            count += 1
    return count


def copy_output_media(run_dir: Path, dest_run: Path) -> int:
    artifacts = run_dir / "task_output" / "artifacts"
    media_dest = dest_run / "output_media"
    if not artifacts.is_dir():
        media_dest.mkdir(parents=True, exist_ok=True)
        return 0
    media_dest.mkdir(parents=True, exist_ok=True)
    count = 0
    for item in artifacts.iterdir():
        if item.name == ARTIFACTS_SCRATCH_DIRNAME:
            continue  # skip scratch frames
        if item.name == ".DS_Store":
            continue
        target = media_dest / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
            count += sum(1 for _ in target.rglob("*") if _.is_file())
        else:
            shutil.copy2(item, target)
            count += 1
    return count


def _run_index_of(run_dirname: str) -> int:
    m = re.search(r"run_(\d+)", run_dirname)
    return int(m.group(1)) if m else 1


def _find_input_task_dir(input_root: Path, task_dir_name: str) -> Path | None:
    if not input_root.is_dir():
        return None
    want = persona_core(task_dir_name)
    candidates = [p for p in input_root.iterdir() if p.is_dir()]
    for p in candidates:
        if persona_core(p.name) == want:
            return p
    for p in candidates:
        if want and want in persona_core(p.name):
            return p
    return None


def _find_ground_truth_source(input_task_dir: Path) -> Path | None:
    """First-match-wins resolution over GROUND_TRUTH_SOURCE_CANDIDATES.

    Returns the path of the first candidate that exists as a regular file,
    or None if none of them exist. Order in the tuple is the priority order:
    GTFA.md (newest) -> golden_steer_flow.md (legacy) -> ground-truth.md
    (already-sliced fallback). Symlinks resolve via is_file()'s follow.
    """
    for name in GROUND_TRUTH_SOURCE_CANDIDATES:
        candidate = input_task_dir / name
        if candidate.is_file():
            return candidate
    return None


def stage_persona_and_artifacts(
    input_task_dir: Path, bundle: Path, verbose: bool
) -> tuple[int, int]:
    env_dir = bundle / "data" / "environment"
    n_persona = 0
    src_persona = input_task_dir / "persona"
    if src_persona.is_dir():
        dest_persona = env_dir / "persona"
        dest_persona.mkdir(parents=True, exist_ok=True)
        # Top-level persona files (SOUL.md, MEMORY.md, USER.md, AGENTS.md, ...)
        # The persona/home/ subdir is intentionally skipped here -- it is
        # the runtime input-artifact source and is handled below alongside
        # <task>/data/ so the bundle mirrors what the agent actually saw.
        for item in src_persona.iterdir():
            if item.is_file() and item.name != ".DS_Store":
                shutil.copy2(item, dest_persona / item.name)
                n_persona += 1

    # Artifact input files: mirror the runtime precedence in
    # src/utils/task_parser.py:340-347 -- <task>/persona/home/ wins if it
    # exists and contains at least one file (recursively); otherwise
    # <task>/data/. Without this, tasks shipping inputs under persona/home/
    # produce bundles whose artifacts/inputs/files/ is empty even though
    # the agent received those files via docker_utils.inject_data_into_workspace.
    n_files = 0
    persona_home = input_task_dir / "persona" / "home"
    data_dir = input_task_dir / "data"
    if persona_home.is_dir() and any(
        p.is_file() for p in persona_home.rglob("*")
    ):
        src_files = persona_home
    elif data_dir.is_dir():
        src_files = data_dir
    else:
        src_files = None

    if src_files is not None:
        dest_files = env_dir.joinpath(*ARTIFACTS_INPUTS_SUBPATH)
        dest_files.mkdir(parents=True, exist_ok=True)
        # rglob preserves nested layout (e.g. persona/home/sub/doc.txt ->
        # artifacts/inputs/files/sub/doc.txt) so multi-level inputs round-trip.
        for item in src_files.rglob("*"):
            if not item.is_file() or item.name == ".DS_Store":
                continue
            rel = item.relative_to(src_files)
            target = dest_files / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
            n_files += 1

    n_harness_env = _stage_harness_env_files(env_dir, verbose)

    if verbose:
        print(
            f"    staged persona: {n_persona} file(s), "
            f"input artifacts: {n_files} file(s), "
            f"harness env: {n_harness_env} file(s)"
        )
    return n_persona, n_files


def _stage_harness_env_files(env_dir: Path, verbose: bool) -> int:
    if not HARNESS_ENV_DIR.is_dir():
        if verbose:
            print(f"    (harness env dir not found at {HARNESS_ENV_DIR}; skipping)")
        return 0
    env_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    for name in HARNESS_ENV_FILES:
        src = HARNESS_ENV_DIR / name
        if src.is_file():
            shutil.copy2(src, env_dir / name)
            n += 1
        elif verbose:
            print(f"    (harness env file missing: {src})")
    return n


def _parse_service_toml(toml_path: Path) -> dict[str, Any] | None:
    try:
        import tomllib
    except ImportError:
        return _parse_service_toml_regex(toml_path)
    try:
        with toml_path.open("rb") as fh:
            doc = tomllib.load(fh)
    except (OSError, Exception):
        return None
    svc = doc.get("service") if isinstance(doc, dict) else None
    if not isinstance(svc, dict):
        return None
    return svc


def _parse_service_toml_regex(toml_path: Path) -> dict[str, Any] | None:
    try:
        text = toml_path.read_text(encoding="utf-8")
    except OSError:
        return None
    in_service = False
    out: dict[str, Any] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            in_service = line == "[service]"
            continue
        if not in_service or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        v = v.strip().strip(",")
        if (v.startswith('"') and v.endswith('"')) or (
            v.startswith("'") and v.endswith("'")
        ):
            out[k] = v[1:-1]
        else:
            try:
                out[k] = int(v)
            except ValueError:
                out[k] = v
    return out or None


def _discover_service_env_vars(
    env_dir: Path, enabled_apis: set[str] | None = None
) -> dict[str, str]:
    out: dict[str, str] = {}
    if not env_dir.is_dir():
        return out
    for sub in sorted(env_dir.iterdir()):
        if not sub.is_dir():
            continue
        if enabled_apis is not None and sub.name not in enabled_apis:
            continue
        toml_path = sub / SERVICE_TOML_FILENAME
        if not toml_path.is_file():
            continue
        svc = _parse_service_toml(toml_path)
        if not svc:
            continue
        env_var_name = svc.get("env_var_name")
        name = svc.get("name") or sub.name
        port = svc.get("port", 8000)
        if not isinstance(env_var_name, str) or not env_var_name:
            continue
        try:
            port_int = int(port)
        except (TypeError, ValueError):
            port_int = 8000
        out[env_var_name] = f"http://{name}:{port_int}"
    return out


def _generate_solve_sh(env_vars: dict[str, str] | None = None) -> str:
    env_vars = dict(env_vars or {})
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "python3 - <<'PY'",
        "import os",
        "",
    ]
    if env_vars:
        for key in sorted(env_vars.keys()):
            default = env_vars[key]
            lvar = key.lower()
            lines.append(
                f"{lvar} = os.environ.get({key!r}, {default!r}).rstrip('/')"
            )
        lines.append("")
    lines.append(
        "print('Solution not yet implemented -- populate with API calls from "
        "golden trajectory.')"
    )
    lines.append("PY")
    return "\n".join(lines) + "\n"


def _generate_test_sh() -> str:
    return _TEST_SH


# ============================================================================
# Harbor-parity emitters: instruction.md + Dockerfile + docker-compose.yaml + task.toml
#
# Background (b1 historical context): src/utils/harbor/bundle.py::write_bundle
# (now dead code, see commit 6e03e6b) emitted four additional files into every
# bundle that this standalone bundler silently dropped after the b1 refactor:
#
#   bundle/data/instruction.md                    (prompt + workspace-hint)
#   bundle/data/environment/Dockerfile            (agent image build recipe)
#   bundle/data/environment/docker-compose.yaml   (mock-stack compose graph)
#   bundle/data/task.toml                         (Harbor task spec metadata)
#
# These are re-emitted here as STDLIB-ONLY inline ports. NEVER replace with
# `from src.utils.harbor.dockerfile import ...` etc. — the standalone-stdlib
# invariant for this script must hold (deliver.sh and run.sh invoke it
# without the eval venv).
#
# Source of truth for the templates:
#   src/utils/harbor/dockerfile.py  (generate_harbor_dockerfile)
#   src/utils/harbor/compose.py     (generate_harbor_compose + runtime_env_defaults)
#   src/utils/harbor/task_toml.py   (build_task_toml + _DEFAULTS)
#   src/utils/task_parser.py:288    (_append_workspace_hint)
#
# Any change in Harbor must be mirrored here in lock-step; the byte-equal
# Harbor parity tests in tests/test_repackage_bundle_test_runners.py will
# fail otherwise. See script/AGENTS.md "4-file emission contract" invariant
# (which already covers test.sh+solve.sh+test_outputs.py+test_weights.json
# and is being extended here to cover the four new emissions).
# ============================================================================

# task_parser.py:288-307 workspace-hint suffix. Appended ONLY when the input
# task ships attachments (persona/home/ files or data/ files); pinned to the
# docker_utils.collect_output_from_container + openclaw assertLocalMediaAllowed
# contract that artifacts MUST be written under /root/workspace/. instruction.md
# must equal what the agent received, so we mirror task_parser semantics.
_WORKSPACE_HINT = (
    "\n\n---\n"
    "Workspace inputs (already staged on disk at `/root/workspace/home` "
    "or `/root/workspace/Home`):\n"
    "Save EVERY output artifact you produce under `/root/workspace/`. "
    "Files written anywhere else (including `/tmp/` and elsewhere under "
    "`/root/`) will NOT be collected as deliverables."
)


def _append_workspace_hint(prompt: str, attachments_present: bool) -> str:
    """Inline port of src/utils/task_parser.py::_append_workspace_hint."""
    if not attachments_present:
        return prompt
    return prompt + _WORKSPACE_HINT


def _detect_attachments_present(input_task_dir: Path) -> bool:
    """Mirror src/utils/task_parser.py:340-347 attachment-detection priority.

    persona/home wins when non-empty (recursively), else data/.
    Returns True iff at least one file would have been mounted into the agent.
    """
    persona_home = input_task_dir / "persona" / "home"
    if persona_home.is_dir():
        for entry in persona_home.rglob("*"):
            if entry.is_file():
                return True
    data_dir = input_task_dir / "data"
    if data_dir.is_dir():
        for entry in data_dir.rglob("*"):
            if entry.is_file():
                return True
    return False


def _resolve_used_apis(input_task_dir: Path | None) -> list[str]:
    """Authoritative list of APIs the task overlays at runtime.

    Sourced from `input/<task>/mock_data/<api>/*` directory names — the same
    ground truth that `src/utils/mock_stack.py::start_mock_stack` uses to mount
    per-task overlays. Returns sorted list. Empty when no mock_data/.
    """
    if input_task_dir is None:
        return []
    mock_data = input_task_dir / "mock_data"
    if not mock_data.is_dir():
        return []
    return sorted(p.name for p in mock_data.iterdir() if p.is_dir())


def _compute_distractor_apis(env_dir: Path, used_apis: list[str]) -> list[str]:
    """Distractor pool = all available APIs in env_dir minus used.

    Mirrors `compute_distractor_skills(required, task_id, count=None)` policy
    (src/utils/skills_inference.py:169): when count is None we publish the
    FULL distractor pool (sorted), matching Harbor's bundle behavior.
    """
    if not env_dir.is_dir():
        return []
    used_set = set(used_apis)
    out = []
    for entry in sorted(env_dir.iterdir()):
        if not entry.is_dir():
            continue
        name = entry.name
        if name in used_set:
            continue
        # An API dir is identified by having a service.toml. Skip persona/
        # artifacts/ skills/ and the 3 harness env .py files (which aren't
        # dirs anyway, but defensive).
        if (entry / SERVICE_TOML_FILENAME).is_file():
            out.append(name)
    return out


# Agent skill mount paths. dockerfile.py:8.
_AGENT_SKILL_DIRS: tuple[str, ...] = (
    "/root/.claude/skills",
    "/root/.codex/skills",
    "/root/.opencode/skills",
    "/root/.goose/skills",
    "/root/.factory/skills",
    "/root/.agents/skills",
    "/root/.gemini/skills",
    "/root/.cursor/skills",
)


def _generate_environment_dockerfile(
    has_skills: bool = False,
    has_persona: bool = False,
    has_artifacts: bool = False,
) -> str:
    """Inline port of src/utils/harbor/dockerfile.py::generate_harbor_dockerfile."""
    lines: list[str] = [
        "FROM ubuntu:24.04",
        "",
        "RUN apt-get update && apt-get install -y --no-install-recommends \\",
        "    curl \\",
        "    jq \\",
        "    python3 \\",
        "    python3-pip \\",
        "    ffmpeg \\",
        "    poppler-utils \\",
        "    ca-certificates \\",
        "    && rm -rf /var/lib/apt/lists/*",
        "",
        "RUN pip install --no-cache-dir --break-system-packages pymupdf pillow",
        "",
    ]
    if has_skills:
        first = _AGENT_SKILL_DIRS[0]
        rest = list(_AGENT_SKILL_DIRS[1:])
        lines += ["# Copy skills to all agent framework paths", "COPY skills %s" % first]
        if rest:
            mkdirs = " ".join(rest)
            copies = " && ".join("cp -a %s/. %s/" % (first, d) for d in rest)
            lines.append("RUN mkdir -p %s && %s" % (mkdirs, copies))
        lines.append("")
    if has_persona:
        lines += ["# Copy persona", "COPY persona /root/.openclaw/persona", ""]
    if has_artifacts:
        lines += [
            "# Copy multimodal artifacts",
            "COPY artifacts/inputs/files /app/artifacts/inputs/files",
            "",
        ]
    lines += ["WORKDIR /app", ""]
    return "\n".join(lines)


# compose.py:25-31 runtime_env_defaults.
_LLM_PROXY_URL = "http://litellm-proxy:4000"
_DEFAULT_CURRENT_DATE = "2026-05-28"


def _compose_runtime_env_defaults() -> dict[str, str]:
    return {
        "LITELLM_BASE_URL": _LLM_PROXY_URL,
        "OPENAI_API_BASE": f"{_LLM_PROXY_URL}/v1",
        "OPENAI_API_KEY": "placeholder",
        "CURRENT_DATE": _DEFAULT_CURRENT_DATE,
    }


def _compose_mem(value: str) -> str:
    """compose.py:_compose_mem. Strip docker-compose's trailing 'i' from Ki/Mi/Gi."""
    if not value:
        return value
    lower = value.lower()
    if lower.endswith(("ki", "mi", "gi")):
        return value[:-1]
    return value


def _compose_healthcheck_cmd(port: int, path: str) -> str:
    """compose.py:_healthcheck_cmd. urllib.request curl-less probe."""
    return (
        f"python3 -c \"import urllib.request,sys; "
        f"sys.exit(0 if urllib.request.urlopen('http://localhost:{port}{path}',"
        f'timeout=3).status<400 else 1)"'
    )


def _parse_service_toml_full(toml_path: Path) -> dict[str, Any] | None:
    """Parse both [service] and [k8s] sections. Returns merged dict for compose.

    Mirrors src/utils/harbor/compose.py::_parse_service_toml (which returns
    name/port/env_var_name/healthcheck_path/k8s_image/cpu_request/memory_request/memory_limit).
    Defaults match Harbor exactly: memory_limit="256Mi" when [k8s].memory_limit absent.
    """
    try:
        import tomllib
    except ImportError:
        tomllib = None
    doc: dict[str, Any] = {}
    if tomllib is not None:
        try:
            with toml_path.open("rb") as fh:
                doc = tomllib.load(fh) or {}
        except Exception:
            doc = {}
    if not doc:
        try:
            text = toml_path.read_text(encoding="utf-8")
        except OSError:
            return None
        section: str | None = None
        for raw in text.splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                section = line[1:-1].strip()
                doc.setdefault(section, {})
                continue
            if section is None or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k = k.strip()
            v = v.strip().strip(",")
            if (v.startswith('"') and v.endswith('"')) or (
                v.startswith("'") and v.endswith("'")
            ):
                doc[section][k] = v[1:-1]
            else:
                try:
                    doc[section][k] = int(v)
                except ValueError:
                    doc[section][k] = v
    svc = doc.get("service", {}) if isinstance(doc, dict) else {}
    k8s = doc.get("k8s", {}) if isinstance(doc, dict) else {}
    if not isinstance(svc, dict):
        svc = {}
    if not isinstance(k8s, dict):
        k8s = {}
    return {
        "name": svc.get("name") or toml_path.parent.name,
        "port": int(svc.get("port") or 8000),
        "env_var_name": svc.get("env_var_name") or "",
        "healthcheck_path": svc.get("healthcheck_path") or "/health",
        "k8s_image": k8s.get("image") or "",
        "cpu_request": k8s.get("cpu_request") or "25m",
        "memory_request": k8s.get("memory_request") or "128Mi",
        "memory_limit": k8s.get("memory_limit") or "256Mi",
    }


def _discover_services_full(env_dir: Path) -> list[dict[str, Any]]:
    """Like _discover_service_env_vars but returns full service records.

    Each record matches Harbor's _parse_service_toml shape: name/port/env_var_name/
    healthcheck_path/k8s_image/cpu_request/memory_request/memory_limit.
    Used by _generate_environment_compose. Memory_limit defaults to "256Mi"
    matching Harbor; this is what triggers the per-service deploy block.
    """
    if not env_dir.is_dir():
        return []
    out: list[dict[str, Any]] = []
    for entry in sorted(env_dir.iterdir()):
        if not entry.is_dir():
            continue
        toml_path = entry / SERVICE_TOML_FILENAME
        if not toml_path.is_file():
            continue
        parsed = _parse_service_toml_full(toml_path)
        if not parsed:
            continue
        out.append(parsed)
    return out


def _generate_environment_compose(
    env_dir: Path,
    services: list[dict[str, Any]] | None = None,
    env_vars: dict[str, str] | None = None,
) -> str:
    """Inline port of src/utils/harbor/compose.py::generate_harbor_compose."""
    if services is None:
        services = _discover_services_full(env_dir)
    if env_vars is None:
        env_vars = {
            svc["env_var_name"]: f"http://{svc['name']}:{svc['port']}"
            for svc in services
            if svc.get("env_var_name")
        }
    svc_list = list(services)

    lines: list[str] = ["services:"]
    lines.append("  main:")
    lines.append("    build:")
    lines.append("      context: .")
    lines.append("    image: harbor-main:local")
    lines.append('    command: ["sleep", "infinity"]')
    lines.append("    environment:")
    for key, value in env_vars.items():
        lines.append(f"      - {key}={value}")
    runtime_env = _compose_runtime_env_defaults()
    lines.append(f"      - LITELLM_BASE_URL={runtime_env['LITELLM_BASE_URL']}")
    lines.append(f"      - OPENAI_API_BASE={runtime_env['OPENAI_API_BASE']}")
    lines.append(f"      - OPENAI_API_KEY={runtime_env['OPENAI_API_KEY']}")
    lines.append("      - LLAMA_API_KEY=${LLAMA_API_KEY}")
    lines.append(f"      - CURRENT_DATE={runtime_env['CURRENT_DATE']}")
    lines.append("      - TEST_DIR=${TEST_DIR:-/tests}")
    lines.append("    volumes:")
    lines.append("      - ${HOST_VERIFIER_LOGS_PATH:-./logs/verifier}:${ENV_VERIFIER_LOGS_PATH:-/logs/verifier}")
    lines.append("      - ${HOST_AGENT_LOGS_PATH:-./logs/agent}:${ENV_AGENT_LOGS_PATH:-/logs/agent}")
    lines.append("    deploy:")
    lines.append("      resources:")
    lines.append("        limits:")
    lines.append("          cpus: \"${CPUS:-1}\"")
    lines.append("          memory: \"${MEMORY:-4096M}\"")
    if svc_list:
        lines.append("    depends_on:")
        for svc in svc_list:
            lines.append(f"      {svc['name']}:")
            lines.append("        condition: service_healthy")

    for svc in svc_list:
        name = svc["name"]
        port = int(svc["port"])
        hpath = svc.get("healthcheck_path") or "/health"
        mem = svc.get("memory_limit") or ""
        lines.append(f"  {name}:")
        lines.append("    build:")
        lines.append(f"      context: ./{name}")
        lines.append(f"    image: harbor-{name}:local")
        lines.append("    expose:")
        lines.append(f"      - \"{port}\"")
        lines.append("    healthcheck:")
        lines.append("      test:")
        lines.append("        - CMD")
        lines.append("        - sh")
        lines.append("        - -c")
        lines.append(f"        - {_compose_healthcheck_cmd(port, hpath)}")
        lines.append("      interval: 5s")
        lines.append("      timeout: 5s")
        lines.append("      retries: 12")
        if mem:
            lines.append("    deploy:")
            lines.append("      resources:")
            lines.append("        limits:")
            lines.append(f"          memory: {_compose_mem(mem)}")

    return "\n".join(lines) + "\n"


# task_toml.py:9-32 _DEFAULTS + _DEFAULT_DIMENSIONS.
_TOML_DEFAULTS: dict[str, Any] = {
    "verifier_timeout_sec": 600,
    "agent_timeout_sec": 900,
    "env_build_timeout_sec": 600,
    "env_cpus": 1,
    "env_memory_mb": 4096,
    "env_storage_mb": 10240,
    "env_allow_internet": True,
    "env_skills_dir": "skills",
    "healthcheck_command": "curl -f http://localhost:8000/health",
    "healthcheck_interval_sec": 5,
    "healthcheck_timeout_sec": 30,
    "healthcheck_retries": 3,
    "pass_at_k": 8,
}
_TOML_DEFAULT_DIMENSIONS: dict[str, Any] = {
    "complex": "medium",
    "long_horizon": False,
    "objective": True,
    "multimodal": True,
    "cross_modal_cross_api": False,
    "asset_complexity": "low",
}


def _q_toml(value: Any) -> str:
    """task_toml.py::_q. Escape and quote a TOML string."""
    s = "" if value is None else str(value)
    s = s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
    return f'"{s}"'


def _arr_toml_strs(values: list[Any]) -> str:
    if not values:
        return "[]"
    parts = ", ".join(_q_toml(v) for v in values)
    return f"[{parts}]"


def _truncate_desc(text: str, limit: int | None = None) -> str:
    """task_toml.py::_truncate_for_description."""
    s = (text or "").replace("\r", "").replace("\n", " ").strip()
    if limit is None or len(s) <= limit:
        return s
    return s[: max(0, limit - 1)].rstrip() + "\u2026"


def _toml_bool(value: bool) -> str:
    return "true" if value else "false"


def _build_task_toml(
    *,
    task_id: str,
    initial_prompt: str,
    required_skills: list[str],
    distractor_skills: list[str],
    env_vars: dict[str, str] | None = None,
    dependency_tags: list[str] | None = None,
    dimensions: dict[str, Any] | None = None,
    verifier_env: dict[str, str] | None = None,
    solution_env: dict[str, str] | None = None,
    pass_at_k: int | None = None,
    healthcheck_command: str | None = None,
    task_type: str = "",
    difficulty: str = "",
) -> str:
    """Inline port of src/utils/harbor/task_toml.py::build_task_toml.

    Sticks to the canonical section order (schema_version, [task], [metadata],
    [verifier], [verifier.env], [agent], [environment], [environment.env],
    [environment.healthcheck], [solution.env], [multimodal], [evaluation],
    [dimensions]). Drift from Harbor's order will break byte-equal tests.
    """
    env_vars = env_vars or {}
    dependency_tags = dependency_tags or []
    dimensions = dict(_TOML_DEFAULT_DIMENSIONS, **(dimensions or {}))
    verifier_env = verifier_env or {}
    solution_env = solution_env or {}
    pass_at_k = pass_at_k if pass_at_k is not None else _TOML_DEFAULTS["pass_at_k"]
    healthcheck_command = healthcheck_command or _TOML_DEFAULTS["healthcheck_command"]
    name = task_id or "kensei2-task"
    description = _truncate_desc(initial_prompt or "")
    keywords = [k for k in (task_type, difficulty) if k]

    lines: list[str] = []
    lines.append('schema_version = "1.1"')
    lines.append("")
    lines.append("[task]")
    lines.append(f"name = {_q_toml(name)}")
    lines.append(f"task_id = {_q_toml(name)}")
    lines.append(f"description = {_q_toml(description)}")
    lines.append(f"keywords = {_arr_toml_strs(keywords)}")
    lines.append("")
    lines.append("[metadata]")
    lines.append(f"category = {_q_toml(task_type)}")
    lines.append(f"difficulty = {_q_toml(difficulty)}")
    lines.append(f"required_skills = {_arr_toml_strs(required_skills)}")
    lines.append(f"distractor_skills = {_arr_toml_strs(distractor_skills)}")
    lines.append("")
    lines.append("[verifier]")
    lines.append(f"timeout_sec = {_TOML_DEFAULTS['verifier_timeout_sec']}")
    lines.append("")
    lines.append("[verifier.env]")
    for k, v in verifier_env.items():
        lines.append(f"{k} = {_q_toml(v)}")
    lines.append("")
    lines.append("[agent]")
    lines.append(f"timeout_sec = {_TOML_DEFAULTS['agent_timeout_sec']}")
    lines.append("")
    lines.append("[environment]")
    lines.append(f"build_timeout_sec = {_TOML_DEFAULTS['env_build_timeout_sec']}")
    lines.append(f"cpus = {_TOML_DEFAULTS['env_cpus']}")
    lines.append(f"memory_mb = {_TOML_DEFAULTS['env_memory_mb']}")
    lines.append(f"storage_mb = {_TOML_DEFAULTS['env_storage_mb']}")
    lines.append(f"allow_internet = {_toml_bool(_TOML_DEFAULTS['env_allow_internet'])}")
    lines.append(f"skills_dir = {_q_toml(_TOML_DEFAULTS['env_skills_dir'])}")
    lines.append("")
    lines.append("[environment.env]")
    for k, v in env_vars.items():
        lines.append(f"{k} = {_q_toml(v)}")
    lines.append("")
    lines.append("[environment.healthcheck]")
    lines.append(f"command = {_q_toml(healthcheck_command)}")
    lines.append(f"interval_sec = {_TOML_DEFAULTS['healthcheck_interval_sec']}")
    lines.append(f"timeout_sec = {_TOML_DEFAULTS['healthcheck_timeout_sec']}")
    lines.append(f"retries = {_TOML_DEFAULTS['healthcheck_retries']}")
    lines.append("")
    lines.append("[solution.env]")
    for k, v in solution_env.items():
        lines.append(f"{k} = {_q_toml(v)}")
    lines.append("")
    lines.append("[multimodal]")
    lines.append(f"dependency_tags = {_arr_toml_strs(dependency_tags)}")
    lines.append("")
    lines.append("[evaluation]")
    lines.append(f"pass_at_k = {pass_at_k}")
    lines.append("")
    lines.append("[dimensions]")
    for key in (
        "complex",
        "long_horizon",
        "objective",
        "multimodal",
        "cross_modal_cross_api",
        "asset_complexity",
    ):
        val = dimensions.get(key, _TOML_DEFAULT_DIMENSIONS[key])
        if isinstance(val, bool):
            lines.append(f"{key} = {_toml_bool(val)}")
        elif isinstance(val, (int, float)):
            lines.append(f"{key} = {val}")
        else:
            lines.append(f"{key} = {_q_toml(val)}")
    lines.append("")
    return "\n".join(lines)


# ============================================================================
# Three new stage helpers: instruction.md, Dockerfile+docker-compose.yaml, task.toml
# Each is fail-soft. Skipped only when their authoritative input is absent.
# ============================================================================


def _stage_data_instruction(
    input_task_dir: Path | None,
    bundle: Path,
    verbose: bool,
) -> bool:
    """Emit bundle/data/instruction.md = prompt.txt + (workspace_hint if attachments).

    Mirrors what the agent received at runtime via task_parser._append_workspace_hint.
    No-op when input_task_dir missing or input_task_dir/prompt.txt missing.
    """
    if input_task_dir is None:
        return False
    prompt_src = input_task_dir / "prompt.txt"
    if not prompt_src.is_file():
        return False
    try:
        prompt_text = prompt_src.read_text(encoding="utf-8")
    except OSError as exc:
        if verbose:
            print(f"    instruction.md skipped: {exc}", file=sys.stderr)
        return False
    attachments = _detect_attachments_present(input_task_dir)
    final_text = _append_workspace_hint(prompt_text, attachments)
    data_dir = bundle / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "instruction.md").write_text(final_text, encoding="utf-8")
    if verbose:
        print(f"    staged instruction.md (attachments={attachments})")
    return True


def _stage_environment_dockerfile_and_compose(
    bundle: Path,
    verbose: bool,
) -> tuple[bool, bool]:
    """Emit bundle/data/environment/Dockerfile and docker-compose.yaml.

    Derives has_skills / has_persona / has_artifacts from the staged
    bundle/data/environment/ tree. Compose service list is also derived from
    that tree (each <api>/service.toml entry). Both files are written
    unconditionally — they're zero-dep on input/<task>/ and reflect what
    the bundle env actually contains. Returns (wrote_dockerfile, wrote_compose).
    """
    env_dir = bundle / "data" / "environment"
    if not env_dir.is_dir():
        return False, False
    has_skills = (env_dir / "skills").is_dir()
    has_persona = (env_dir / "persona").is_dir()
    has_artifacts = (env_dir / "artifacts" / "inputs" / "files").is_dir()
    dockerfile_text = _generate_environment_dockerfile(
        has_skills=has_skills,
        has_persona=has_persona,
        has_artifacts=has_artifacts,
    )
    (env_dir / "Dockerfile").write_text(dockerfile_text, encoding="utf-8")
    services = _discover_services_full(env_dir)
    env_vars = {
        svc["env_var_name"]: f"http://{svc['name']}:{svc['port']}"
        for svc in services
        if svc.get("env_var_name")
    }
    compose_text = _generate_environment_compose(env_dir, services=services, env_vars=env_vars)
    (env_dir / "docker-compose.yaml").write_text(compose_text, encoding="utf-8")
    if verbose:
        print(
            f"    staged environment/Dockerfile + docker-compose.yaml "
            f"(skills={has_skills} persona={has_persona} artifacts={has_artifacts} "
            f"services={len(services)})"
        )
    return True, True


_L_TAG_RE = re.compile(r"^\s*(l1|l2)\s*:\s*(.+?)\s*$", re.MULTILINE)


def _resolve_dependency_tags(input_task_dir: Path | None) -> list[str]:
    """Multimodal dependency_tags = [l1, l2] sourced from input/<task>/task.yaml.

    Mirrors Harbor bundle.py:_dependency_tags — the l1 then l2 *values* in order,
    dropping any that are blank. Fail-soft: returns [] when task.yaml is absent or
    unreadable, or when neither tag is present. Stdlib-only (no PyYAML) per the
    standalone-stdlib invariant; the flat `key: value` schema in task.yaml is
    simple enough that a regex match is safer than a third-party YAML parser.
    """
    if input_task_dir is None:
        return []
    task_yaml = input_task_dir / "task.yaml"
    if not task_yaml.is_file():
        return []
    try:
        text = task_yaml.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    found: dict[str, str] = {}
    for key, raw in _L_TAG_RE.findall(text):
        if key not in found:
            found[key] = raw.strip().strip("'\"").strip()
    return [v for v in (found.get("l1"), found.get("l2")) if v]


def _stage_task_toml(
    input_task_dir: Path | None,
    bundle: Path,
    verbose: bool,
    pass_at_k: int | None = None,
) -> bool:
    """Emit bundle/data/task.toml using Harbor-parity build_task_toml port.

    Resolution policy (matches Harbor bundle.py:171-253):
      - required = input/<task>/mock_data/<api>/ dir names (sorted)
      - distractor = bundle/data/environment/ APIs minus required
      - env_vars = filtered_services (required ∪ distractor)
      - healthcheck_command = ' && '.join('curl -f http://localhost:{port}/health' per filtered svc)
      - environment_env = env_vars + runtime_env_defaults()
      - verifier_env = environment_env + {TEST_DIR:/tests}
      - solution_env = environment_env
      - required_skills = [f'{n}-connector' for n in required]
      - distractor_skills = [f'{n}-connector' for n in distractor]
      - multimodal = bool(attachments_present)
    No-op when input_task_dir missing OR input_task_dir/prompt.txt missing.
    """
    if input_task_dir is None:
        return False
    prompt_src = input_task_dir / "prompt.txt"
    if not prompt_src.is_file():
        return False
    try:
        prompt_text = prompt_src.read_text(encoding="utf-8")
    except OSError:
        prompt_text = ""

    used_apis = _resolve_used_apis(input_task_dir)
    bundle_env_dir = bundle / "data" / "environment"
    distractor_apis = _compute_distractor_apis(bundle_env_dir, used_apis)
    used_with_distractor = set(used_apis) | set(distractor_apis)

    all_services = _discover_services_full(bundle_env_dir)
    filtered = [s for s in all_services if s["name"] in used_with_distractor]
    env_vars = {
        svc["env_var_name"]: f"http://{svc['name']}:{svc['port']}"
        for svc in filtered
        if svc.get("env_var_name")
    }
    healthcheck_cmd = (
        " && ".join(
            f"curl -f http://localhost:{svc['port']}{svc.get('healthcheck_path') or '/health'}"
            for svc in filtered
        )
        or _TOML_DEFAULTS["healthcheck_command"]
    )
    runtime_env = _compose_runtime_env_defaults()
    environment_env = {**env_vars, **runtime_env}
    verifier_env = {**environment_env, "TEST_DIR": "/tests"}
    solution_env = dict(environment_env)

    required_skills = [f"{name}-connector" for name in used_apis]
    distractor_skills = [f"{name}-connector" for name in distractor_apis]

    attachments_present = _detect_attachments_present(input_task_dir)
    dimensions = {
        "multimodal": attachments_present,
    }
    dependency_tags = _resolve_dependency_tags(input_task_dir)

    toml_text = _build_task_toml(
        task_id=input_task_dir.name,
        initial_prompt=prompt_text,
        required_skills=required_skills,
        distractor_skills=distractor_skills,
        env_vars=environment_env,
        dependency_tags=dependency_tags,
        dimensions=dimensions,
        verifier_env=verifier_env,
        solution_env=solution_env,
        pass_at_k=pass_at_k,
        healthcheck_command=healthcheck_cmd,
    )
    data_dir = bundle / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "task.toml").write_text(toml_text, encoding="utf-8")
    if verbose:
        print(
            f"    staged task.toml (required={len(required_skills)} "
            f"distractor={len(distractor_skills)} env_vars={len(env_vars)} "
            f"dependency_tags={dependency_tags})"
        )
    return True


def _stage_test_runners_and_solver(
    input_task_dir: Path | None,
    bundle: Path,
    verbose: bool,
) -> tuple[bool, bool, bool, bool]:
    """Stage data/tests/{test_outputs.py,test_weights.json,test.sh} + data/solution/solve.sh.

    Returns (had_outputs, had_weights, wrote_test_sh, wrote_solve_sh) for verbose reporting.
    test.sh and solve.sh are always emitted (zero-dep on input/). test_outputs.py
    and test_weights.json are emitted only when present at the input task root.
    """
    tests_dir = bundle / "data" / TESTS_SUBDIR
    solution_dir = bundle / "data" / SOLUTION_SUBDIR

    had_outputs = False
    had_weights = False
    if input_task_dir is not None:
        src_outputs = _resolve_test_outputs_source(input_task_dir)
        if src_outputs is not None:
            tests_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_outputs, tests_dir / TEST_OUTPUTS_FILENAME)
            had_outputs = True
        src_weights = input_task_dir / TEST_WEIGHTS_FILENAME
        if src_weights.is_file():
            tests_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_weights, tests_dir / TEST_WEIGHTS_FILENAME)
            had_weights = True

    tests_dir.mkdir(parents=True, exist_ok=True)
    (tests_dir / TEST_SH_FILENAME).write_text(_generate_test_sh(), encoding="utf-8")
    wrote_test_sh = True

    bundle_env_dir = bundle / "data" / "environment"
    env_vars = _discover_service_env_vars(bundle_env_dir, enabled_apis=None)
    solution_dir.mkdir(parents=True, exist_ok=True)
    (solution_dir / SOLVE_SH_FILENAME).write_text(
        _generate_solve_sh(env_vars), encoding="utf-8"
    )
    wrote_solve_sh = True

    if verbose:
        print(
            f"    staged test runners: outputs={had_outputs} weights={had_weights} "
            f"test.sh={wrote_test_sh} solve.sh={wrote_solve_sh} (env_vars={len(env_vars)})"
        )
    return had_outputs, had_weights, wrote_test_sh, wrote_solve_sh


# Basename-anywhere patterns stripped from the copied data/ tree. NOTE: "scripts"
# is deliberately NOT here — see _bundle_data_ignore. ignore_patterns matches a
# basename at every depth, so a blanket "scripts" would also delete every
# skills/<connector>/scripts/ dir (the connector helper scripts), not just the
# repo dev-tooling environment/scripts/ dir we actually want gone.
_BUNDLE_DATA_IGNORE_NAMES = shutil.ignore_patterns(
    "litellm-proxy",
    "API_DOCUMENTATION.md",
    "sqlite_mcp_server.db",
    "tracking_middleware.py",
    "_meta.json",
    "_overlay_manifest.json",
    "__pycache__",
    "*.pyc",
    # Internal R&D meta-skill under environment/skills/. Reference delivery shows
    # 104 skills; ours had 105 with this extra. Added 2026-06-27 per user m1008.
    "self-improving-agent-*",
)


def _bundle_data_ignore(dir: str, names: list[str]) -> set[str]:
    """copytree ignore: the name patterns above, plus environment/scripts ONLY.

    The repo dev-tooling dir environment/scripts/ (audit_data_formats.py,
    migrate_csv_to_json.py, wiring_report.*, ...) must be stripped, but the
    per-connector skills/<name>/scripts/ dirs must survive. A path-aware check
    drops `scripts` only when it sits directly under environment/.
    """
    ignored = set(_BUNDLE_DATA_IGNORE_NAMES(dir, names))
    if Path(dir).name == "environment" and "scripts" in names:
        ignored.add("scripts")
    return ignored


def _backfill_skill_scripts_from_baseline(bundle_env_dir: Path, verbose: bool) -> int:
    """Backfill missing `skills/<connector>/scripts/` from <repo>/environment/.

    The bundler sources skills from `output/<task>/data/environment/skills/`,
    which is populated at run time by `src/utils/env_overlay_snapshot.py`.
    If that stage didn't run (legacy outputs predating b63, manual re-bundle
    of stale `output/` trees, etc.), per-connector `scripts/` dirs may be
    missing from the output AND therefore from the bundle.

    To guarantee deliverable bundles always carry per-connector helper
    scripts (e.g. `fetch_<api>_data.py`), we backfill ONLY missing
    `scripts/` subdirs from the canonical baseline at
    `<repo>/environment/skills/<connector>/scripts/`. Existing bundle
    scripts/ dirs are NEVER overwritten -- preserves any per-task
    overlay/mutation. The top-level `environment/scripts/` dev-tooling dir
    is NOT backfilled.

    Returns the number of connector scripts/ dirs backfilled.
    """
    bundle_skills = bundle_env_dir / "skills"
    baseline_skills = HARNESS_ENV_DIR / "skills"
    if not bundle_skills.is_dir() or not baseline_skills.is_dir():
        return 0
    backfilled = 0
    for bundle_skill in sorted(bundle_skills.iterdir()):
        if not bundle_skill.is_dir():
            continue
        if not bundle_skill.name.endswith("-connector"):
            continue
        scripts_dst = bundle_skill / "scripts"
        if scripts_dst.exists():
            continue
        scripts_src = baseline_skills / bundle_skill.name / "scripts"
        if not scripts_src.is_dir():
            continue
        try:
            shutil.copytree(
                scripts_src,
                scripts_dst,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            backfilled += 1
        except OSError as exc:
            if verbose:
                print(f"    backfill failed for {bundle_skill.name}/scripts: {exc}")
    if verbose and backfilled:
        print(f"    backfilled {backfilled} connector scripts/ dir(s) from <repo>/environment/skills/")
    return backfilled


def convert_task(
    task_dir: Path,
    dest_root: Path,
    input_root: Path,
    infer_meta: bool,
    verbose: bool,
    latest_only: bool = False,
) -> Path | None:
    trajectories = task_dir / "trajectories"
    if not trajectories.is_dir():
        print(f"  ! no trajectories/ under {task_dir.name}; skipping", file=sys.stderr)
        return None

    bundle = dest_root / task_dir.name
    # rubric.json + data/ come from the run-output task dir; prompt.txt is
    # re-sourced from the original input task dir (data/ minus litellm-proxy).
    if (task_dir / "rubric.json").exists():
        bundle.mkdir(parents=True, exist_ok=True)
        shutil.copy2(task_dir / "rubric.json", bundle / "rubric.json")
    if (task_dir / "data").is_dir():
        shutil.copytree(
            task_dir / "data",
            bundle / "data",
            dirs_exist_ok=True,
            ignore=_bundle_data_ignore,
        )
        _backfill_skill_scripts_from_baseline(bundle / "data" / "environment", verbose)

    # Re-source prompt.txt, persona/ and staged input files (stripped/altered in
    # run output) from the original input task dir, fuzzy-matched by persona core.
    input_task_dir = _find_input_task_dir(input_root, task_dir.name)
    if input_task_dir is not None:
        prompt_src = input_task_dir / "prompt.txt"
        if prompt_src.exists():
            bundle.mkdir(parents=True, exist_ok=True)
            shutil.copy2(prompt_src, bundle / "prompt.txt")
        # Ground truth: publish a SLICE of the source flow doc as ground-truth.md.
        # Source is whichever of GROUND_TRUTH_SOURCE_CANDIDATES exists first.
        # Only the Focal Event / Canonical Solve Path / Value Lock sections are
        # extracted; the rest of the author-side flow doc is intentionally not
        # leaked into the bundle. See extract_ground_truth_sections().
        steer_src = _find_ground_truth_source(input_task_dir)
        if steer_src is None:
            print(
                f"  ! {task_dir.name}: no ground-truth source file found in "
                f"{input_task_dir} (looked for: "
                f"{', '.join(GROUND_TRUTH_SOURCE_CANDIDATES)}); "
                f"skipping {GROUND_TRUTH_FILENAME}",
                file=sys.stderr,
            )
        else:
            try:
                steer_text = steer_src.read_text(encoding="utf-8")
            except OSError as exc:
                steer_text = ""
                print(
                    f"  ! {task_dir.name}: failed to read {steer_src.name} "
                    f"({exc}); skipping {GROUND_TRUTH_FILENAME}",
                    file=sys.stderr,
                )
            extracted = extract_ground_truth_sections(steer_text)
            if extracted:
                bundle.mkdir(parents=True, exist_ok=True)
                (bundle / GROUND_TRUTH_FILENAME).write_text(extracted, encoding="utf-8")
                if verbose:
                    print(
                        f"    staged ground truth: {steer_src.name} -> "
                        f"{GROUND_TRUTH_FILENAME} (sliced)"
                    )
            elif steer_text:
                print(
                    f"  ! {task_dir.name}: {steer_src.name} present but "
                    f"no target sections (Focal Event / Canonical Solve Path / "
                    f"Value Lock) matched; skipping {GROUND_TRUTH_FILENAME}",
                    file=sys.stderr,
                )
        stage_persona_and_artifacts(input_task_dir, bundle, verbose)
    elif verbose:
        print(f"    (no input dir matched under {input_root}; prompt/persona/artifacts skipped)")

    _stage_test_runners_and_solver(input_task_dir, bundle, verbose)
    _stage_data_instruction(input_task_dir, bundle, verbose)
    _stage_environment_dockerfile_and_compose(bundle, verbose)
    _stage_task_toml(input_task_dir, bundle, verbose)

    produced_any = False
    for harness_dir in sorted(p for p in trajectories.iterdir() if p.is_dir()):
        pretty = _pretty_model(harness_dir.name)
        dest_model = bundle / "trajectories" / pretty
        run_dirs = sorted(
            (p for p in harness_dir.iterdir() if p.is_dir() and re.match(r"run_\d+", p.name)),
            key=lambda p: _run_index_of(p.name),
        )
        if latest_only and run_dirs:
            run_dirs = [run_dirs[-1]]
        per_run_summ: list[dict[str, Any]] = []
        for run_dir in run_dirs:
            ridx = _run_index_of(run_dir.name)
            dest_run = dest_model / f"run_{ridx}"
            dest_run.mkdir(parents=True, exist_ok=True)

            # 1) output.json copied as-is
            src_out = run_dir / "output.json"
            if src_out.exists():
                shutil.copy2(src_out, dest_run / "output.json")

            # 2) logs/verifier/ copied as-is (raw ctrf.json, test_weights.json,
            #    reward.txt and siblings — see copy_verifier_logs docstring)
            n_verifier = copy_verifier_logs(run_dir, dest_run)
            _stage_verifier_test_sources(
                input_task_dir, dest_run / "logs" / "verifier", verbose
            )

            # 3) report.json built
            report = build_report(run_dir, task_dir, pretty, ridx, infer_meta)
            _write_json(dest_run / "report.json", report)

            # 4) output_media
            n_media = copy_output_media(run_dir, dest_run)

            # 5) subagents/ + spawn_tree/ — native multi-agent child
            #    trajectories and the spawn tree (empty subagents/ dir for
            #    single-agent runs so the multi-agent validator passes)
            copy_subagent_artifacts(run_dir, dest_run)

            per_run_summ.append(
                {
                    "run_index": ridx,
                    "include_multimodal": report["include_multimodal"],
                    "test_weights_percentage": report["test_weights_percentage"],
                    "rubric_weights_percentage": report["rubric_weights_percentage"],
                }
            )
            produced_any = True
            if verbose:
                print(
                    f"    {pretty}/run_{ridx}: report.json + output.json "
                    f"+ {n_verifier} verifier file(s) + {n_media} media file(s)"
                )

        # pass_summary.json REBUILT from the runs we actually emitted.
        if per_run_summ:
            n = len(per_run_summ)
            avg_test = sum(r["test_weights_percentage"] for r in per_run_summ) / n
            avg_rub = sum(r["rubric_weights_percentage"] for r in per_run_summ) / n
            _write_json(
                dest_model / "pass_summary.json",
                {
                    "model": pretty,
                    "runs": n,
                    "average_test_weights_percentage": round(avg_test, 2),
                    "average_rubric_weights_percentage": round(avg_rub, 2),
                    "per_run": per_run_summ,
                },
            )

    if produced_any:
        print(f"  + {task_dir.name}  ->  {bundle}")
        return bundle
    print(f"  ! {task_dir.name}: no run_N dirs found; nothing emitted", file=sys.stderr)
    return None


def discover_tasks(source_root: Path) -> list[Path]:
    return sorted(
        p for p in source_root.iterdir()
        if p.is_dir() and (p / "trajectories").is_dir()
    )


def select_tasks(source_root: Path, persona: str | None, do_all: bool) -> list[Path]:
    tasks = discover_tasks(source_root)
    if do_all:
        return tasks
    want = persona_core(persona or "")
    matches = [t for t in tasks if persona_core(t.name) == want]
    if not matches:
        # Looser fallback: substring on core key, so "ben" matches "ben cox".
        matches = [t for t in tasks if want and want in persona_core(t.name)]
    return matches


# =============================================================================
# Output-side data staging (parity with bundle/data/)
# =============================================================================
#
# Why this exists:
#   `output/<backend>/<task>/data/` was a runtime scratch tree (only contained
#   raw env baseline + per-task overlay snapshot + the _overlay_manifest.json
#   sidecar). The bundle's `data/` (built by `convert_task` -> bundle.root)
#   was a superset: it ALSO contained
#     - data/environment/{tracking_middleware,admin_plane,_mutable_store}.py
#       (from <repo>/environment/)
#     - data/environment/persona/* (from input/<task>/persona/)
#     - data/environment/artifacts/inputs/files/** (from input/<task>/persona/home
#       or input/<task>/data/)
#     - data/tests/{test.sh,test_outputs.py,test_weights.json}
#     - data/solution/solve.sh
#
# `stage_output_data` writes the SAME 5 staging artifacts into the source
# `output/<backend>/<task>/data/` tree so that `output/<task>/data` and
# `output_bundle/<task>/data` become byte-equal modulo the three by-design
# strips (`_overlay_manifest.json`, `_meta.json`, `skills/*/_meta.json`).
#
# Implementation strategy: reuse `stage_persona_and_artifacts` and
# `_stage_test_runners_and_solver` verbatim by passing `task_dir` as the
# `bundle` arg. Both helpers write to `<bundle>/data/...`, so the writes
# land in `<task_dir>/data/...` -- exactly the parity we want.
#
# Caller contract: invoked by `eval/run_batch.py::_build_trajectory` via
# subprocess AFTER the agent run completes BUT BEFORE the bundler subprocess
# call. The bundler's `shutil.copytree(task_dir/'data', bundle/'data', ...)`
# at L1173-1186 then propagates the staged tree into the bundle naturally,
# so the bundler's own subsequent calls to `stage_persona_and_artifacts` and
# `_stage_test_runners_and_solver` become idempotent backfills (no harm).
# =============================================================================
def stage_output_data(
    task_dir: Path,
    input_root: Path,
    verbose: bool = False,
) -> bool:
    """Stage the 5 mirror-into-output artifacts into ``task_dir/data/``.

    Returns True on success (best-effort: missing input dir doesn't fail).
    Always emits ``data/tests/test.sh`` and ``data/solution/solve.sh`` (they
    have zero dependency on ``input/<task>/``); the rest are conditional on
    an input task dir match.
    """
    if not task_dir.is_dir():
        print(f"error: task_dir not a directory: {task_dir}", file=sys.stderr)
        return False

    input_task_dir = _find_input_task_dir(input_root, task_dir.name)
    if input_task_dir is None and verbose:
        print(
            f"    (no input dir matched under {input_root}; "
            f"persona/artifacts/test_outputs/test_weights skipped; "
            f"test.sh + solve.sh still emitted)"
        )

    # When input_task_dir is None we still want test.sh + solve.sh emitted
    # into task_dir/data/{tests,solution}/. stage_persona_and_artifacts
    # requires a non-None input_task_dir, so we only call it when present.
    if input_task_dir is not None:
        stage_persona_and_artifacts(input_task_dir, task_dir, verbose)

    _stage_test_runners_and_solver(input_task_dir, task_dir, verbose)
    _stage_data_instruction(input_task_dir, task_dir, verbose)
    _stage_environment_dockerfile_and_compose(task_dir, verbose)
    _stage_task_toml(input_task_dir, task_dir, verbose)
    return True


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Repackage raw run output into the published bundle structure.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--source-root",
        default="output/openclaw",
        help="Root containing raw <task_id>/ dirs (default: output/openclaw)",
    )
    ap.add_argument(
        "--dest-root",
        help="Destination root for the published bundle tree (created if absent). "
        "Required for bundle mode; ignored for --stage-output-data.",
    )
    ap.add_argument(
        "--input-root",
        default="input",
        help="Root of original task input dirs, used to re-source persona/ and "
        "staged input files (default: input).",
    )
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument(
        "--persona",
        help='Persona core name to convert, fuzzy-matched (e.g. "ben cox").',
    )
    grp.add_argument(
        "--all", action="store_true", help="Convert every task under --source-root."
    )
    ap.add_argument(
        "--infer-rubric-meta",
        action="store_true",
        help="Heuristically fill rubric type/evaluation_target (else left empty).",
    )
    # --stage-output-data: alternate mode. Instead of writing a bundle under
    # --dest-root, stage the 5 mirror artifacts (harness env .py files,
    # persona/, artifacts/inputs/files/, tests/, solution/) directly into
    # the SOURCE output/<task>/data/ tree so it matches the bundle's data/
    # modulo the 3 by-design strips. See `stage_output_data` docstring.
    ap.add_argument(
        "--stage-output-data",
        action="store_true",
        help="Mirror persona/artifacts/harness-env/tests/solution into the SOURCE "
        "output/<task>/data/ tree (no bundle written; --dest-root ignored).",
    )
    ap.add_argument("-v", "--verbose", action="store_true", help="Per-run detail.")
    # All valid runs are published by default. --all-runs is kept as a no-op
    # alias for backward compatibility with older invocations/scripts.
    ap.add_argument(
        "--all-runs",
        action="store_true",
        help="(Default) Publish every valid run per model. Retained for "
        "backward compatibility; all runs are emitted unless --latest-only.",
    )
    ap.add_argument(
        "--latest-only",
        action="store_true",
        help="Publish only the single latest valid run per model (highest "
        "run_N). Default is to publish all runs.",
    )
    args = ap.parse_args(argv)

    source_root = Path(args.source_root).resolve()
    input_root = Path(args.input_root).resolve()
    if not source_root.is_dir():
        print(f"error: --source-root not a directory: {source_root}", file=sys.stderr)
        return 2

    tasks = select_tasks(source_root, args.persona, args.all)
    if not tasks:
        avail = ", ".join(sorted(persona_core(t.name) for t in discover_tasks(source_root))) or "(none)"
        print(
            f"error: no task matched persona {args.persona!r}. "
            f"Available persona cores: {avail}",
            file=sys.stderr,
        )
        return 1

    if args.stage_output_data:
        print(f"source : {source_root}")
        print(f"input  : {input_root}")
        print(f"mode   : stage-output-data ({len(tasks)} task(s))")
        produced = 0
        for task_dir in tasks:
            if stage_output_data(task_dir, input_root, args.verbose):
                produced += 1
        print(f"done: staged output data for {produced}/{len(tasks)} task(s)")
        return 0 if produced else 1

    if not args.dest_root:
        print("error: --dest-root is required in bundle mode", file=sys.stderr)
        return 2
    dest_root = Path(args.dest_root).resolve()

    print(f"source : {source_root}")
    print(f"dest   : {dest_root}")
    print(f"input  : {input_root}")
    print(f"tasks  : {len(tasks)} selected")
    dest_root.mkdir(parents=True, exist_ok=True)
    produced = 0
    for task_dir in tasks:
        if convert_task(task_dir, dest_root, input_root, args.infer_rubric_meta, args.verbose,
                        latest_only=args.latest_only):
            produced += 1
    print(f"done: {produced}/{len(tasks)} task bundle(s) written under {dest_root}")
    return 0 if produced else 1


if __name__ == "__main__":
    raise SystemExit(main())
