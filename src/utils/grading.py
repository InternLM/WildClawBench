from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Sequence
from typing import Literal
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()
TMP_WORKSPACE = os.environ.get("TMP_WORKSPACE", "/tmp_workspace")


# ---------------------------------------------------------------------------
# LLM rubric judge (for native prompt.txt + rubric.json tasks)
#
# Native tasks have no `automated_checks` to exec, so without this they score a
# degenerate reward:0.0 / tests_total:0 no matter how well the agent did. This
# judge scores each rubric criterion 0..1 against the agent's deliverables +
# transcript, then weights them into an overall_score and per-criterion test
# counts. Transport selection (m1612):
#   * DEFAULT — direct urllib POST to OpenAI / Bedrock-Converse from the host.
#     The per-batch LiteLLM SIDECAR is not host-reachable (--internal bridge,
#     no published port); the host can reach both providers directly (verified).
#   * OPT-IN — when KENSEI_JUDGE_USE_LITELLM=true, the dispatcher routes through
#     LiteLLM in *library mode* (in-process `litellm.completion`) via
#     `src/utils/judge_litellm.py`, with optional Headroom user-turn compression
#     gated by KENSEI_JUDGE_HEADROOM_ENABLED. On ANY LiteLLM/Headroom error the
#     dispatcher falls through to the urllib path so grading never fails because
#     of transport choice. Both transports MUST produce the same 7-key per-judge
#     `usage` dict (input/output/cache_read/cache_write/total tokens, request_count,
#     cost_usd); LiteLLM path adds an OPTIONAL `headroom` sub-dict aggregated into
#     `score.json.judge_council.headroom_per_member`.
# Fully best-effort: any failure returns a structured error and never raises
# into the run loop.
# ---------------------------------------------------------------------------

# JUDGE_MODEL / JUDGE_MODEL_FALLBACK envs are no longer consulted (m1609):
# single-judge mode was removed and the council is the only grading path.
# Configure council members via JUDGE_COUNCIL_MEMBERS or the per-judge
# JUDGE_COUNCIL_SONNET_ARN / _GLM_ARN / _KIMI_ARN env vars (resolved live by
# council_members(); see the FAMILY decoupling block below).
# Smallest-member-governs evidence cap, derived from AWS Bedrock official
# context-window numbers (2026-06-02 web-confirmed, no longer hit-and-trial):
#   * Claude Sonnet 4.6 (is9bst5tfadh) — 1,000,000 input tokens
#   * Kimi K2.5         (p532c9fzmeed) —   256,000 input tokens
#   * GLM 5             (xx5msvho23iq) —   200,000 input tokens  <-- smallest
# Bedrock enforces input_tokens + max_tokens <= context_window (see LiteLLM
# PR #22479 / issue #22478). Our maxTokens request is 4,000. Empirical chars
# /token ratio on real WildClawBench payloads is ~2.515 (500k chars produced
# 198,753 input tokens for GLM in the m1037 probe). Budget:
#   200,000 ctx  − 4,000 output  − ~5,000 scaffold (TASK + 25-rubric criteria
#   + JSON schema + system prompt) = ~191,000 tokens for evidence
#   ÷ 2.515 chars/token = ~75,944 evidence tokens worth of chars ≈ 191,000
# Converting back: 191,000 tokens × 2.515 chars/token ≈ 480,365 chars. Round
# down with safety margin for tokenizer drift and rubric-block variance:
# 450,000 chars. Operators with a single high-context judge (Sonnet's 1M
# budget) can lift this by exporting JUDGE_MAX_EVIDENCE=<chars>. Setting it
# to 0 (or anything falsy after int()) restores the unbounded behavior we
# briefly defaulted to between b31 and now — known to 400 every council
# member on real WildClawBench runs.
_DEFAULT_JUDGE_MAX_EVIDENCE = 450_000

# Claude via the OAuth subscription bridge has a HARD 200,000-token context
# window (api.anthropic.com), NOT the 1,000,000-token Bedrock Sonnet profile the
# rotating ARN points at. The per-family Sonnet budget (1,350,000 chars in
# _FAMILY_EVIDENCE) is sized for that 1M Bedrock window and blows past 200K
# tokens on large trajectories, which then falls back to the tokenless
# urllib/Bedrock path and fails with "no Bedrock bearer token".
#
# We budget by CHARS but the ceiling is in TOKENS, and the chars/token ratio is
# NOT constant — it depends on how token-dense the trajectory is:
#   * kayla run_4 (prose-ish):   545K chars → 139K tokens  (~3.9 chars/token)
#   * kayla run_1 (JSON-dense):  405K chars → 217K tokens  (~1.87 chars/token) → 400
# So a char cap must survive the WORST-case (~1.8 chars/token) density. An earlier
# 600K cap failed: 405K evidence chars alone already hit 216,921 tokens > 200,000.
# Target a safe ~160K-token input ceiling (leaving margin under 200K for
# system(~7K)+rubric+criteria+output(8K) and any density spikes):
#   160,000 tokens × 1.8 chars/token ≈ 288,000 chars  → round to 300,000.
# At worst-case density that is ~167K tokens; at run_4 density only ~77K tokens
# (still ample evidence + Headroom compression runs on top). Tunable via
# KENSEI_JUDGE_OAUTH_MAX_EVIDENCE for trajectories that are even denser.
_DEFAULT_JUDGE_OAUTH_MAX_EVIDENCE = 300_000


def _judge_oauth_max_evidence() -> int:
    raw = os.environ.get("KENSEI_JUDGE_OAUTH_MAX_EVIDENCE")
    if raw is None or raw.strip() == "":
        return _DEFAULT_JUDGE_OAUTH_MAX_EVIDENCE
    try:
        n = int(raw)
    except ValueError:
        return _DEFAULT_JUDGE_OAUTH_MAX_EVIDENCE
    return n if n > 0 else _DEFAULT_JUDGE_OAUTH_MAX_EVIDENCE


def _resolve_judge_max_evidence() -> int | None:
    raw = os.environ.get("JUDGE_MAX_EVIDENCE")
    if raw is None or raw.strip() == "":
        return _DEFAULT_JUDGE_MAX_EVIDENCE
    try:
        n = int(raw)
    except ValueError:
        return _DEFAULT_JUDGE_MAX_EVIDENCE
    return n if n > 0 else None


_JUDGE_MAX_EVIDENCE = _resolve_judge_max_evidence()

# Per-member evidence budgets (chars). Council members have different context
# windows, so each gets a payload sized to its own ceiling instead of all three
# sharing the smallest-member cap. Numbers derived from the same arithmetic as
# _DEFAULT_JUDGE_MAX_EVIDENCE:
#   budget_chars = (ctx_window − 4,000 maxTokens − ~5,500 scaffold) × 2.515 chars/token
# Rounded down with safety margin for tokenizer drift and rubric-block variance.
# Match patterns are checked against the model identifier as-passed, so an
# operator override via JUDGE_COUNCIL_*_ARN still maps to the correct budget so
# long as the inference-profile ID stays in the string.
# AWS edge body cap (~25 MB) observed in (b40) probes B2/B3 caps every Bedrock
# request regardless of context window; we cap at 24,000,000 chars to leave
# headroom for JSON envelope + scaffold + base64 overhead.
_AWS_EDGE_BODY_CAP = 24_000_000

# Fallback for unrecognized models (single-judge OpenAI fallback, custom ARNs).
# OpenAI auto-caches and has its own server-side enforcement; conservative.
# Per-family (budget_chars, max_output_tokens) live in _FAMILY_EVIDENCE below.
_DEFAULT_MAX_OUTPUT_TOKENS = 4000


# ── Council member FAMILY decoupling (profile-ID rotation) ──────────────────
# Company policy rotates the three Bedrock judge inference-profile ARNs MONTHLY,
# which changes the opaque profile-id suffix (e.g. is9bst5tfadh) every rotation.
# Therefore the profile id is NOT a stable key: pricing / evidence-budget /
# cache-eligibility must be keyed by a STABLE logical *family* label instead, and
# the rotating ARN is supplied at runtime from .env. The family of a council
# member is derived from the FIXED env-var NAME that carries its ARN
# (JUDGE_COUNCIL_SONNET_ARN → "sonnet", _GLM_ARN → "glm", _KIMI_ARN → "kimi"),
# never by parsing the rotating id. See .env.example and tests/test_judge_rotation.py.
JudgeFamily = Literal["sonnet", "glm", "kimi"]

# Stable env-var → family dispatch. Order is the canonical council order.
_FAMILY_ENV_VARS: tuple[tuple[str, str], ...] = (
    ("sonnet", "JUDGE_COUNCIL_SONNET_ARN"),
    ("glm", "JUDGE_COUNCIL_GLM_ARN"),
    ("kimi", "JUDGE_COUNCIL_KIMI_ARN"),
)
_KNOWN_FAMILIES: frozenset[str] = frozenset(fam for fam, _ in _FAMILY_ENV_VARS)

# Per-family per-token rates (input, output, cache_read, cache_write) USD/token.
# Source of truth for council billing — web-verified against AWS published cards
# (see _JUDGE_RATES header). judge_litellm.register_judges_for_batch imports THIS
# table so the two transports cannot drift (was the G15 drift bug). Values must
# track real published prices, not the (rotating) profile id.
#   Sonnet 4.6: $3/$15/$3.75cw/$0.30cr   GLM-5: $1.00/$3.20(+$0.20cr)   Kimi K2.5: $0.72/$3.60
_FAMILY_RATES: dict[str, tuple[float, float, float, float]] = {
    "sonnet": (3e-6, 1.5e-5, 3e-7, 3.75e-6),
    "glm": (1e-6, 3.2e-6, 2e-7, 0.0),
    "kimi": (0.72e-6, 3.6e-6, 0.0, 0.0),
}
# Per-family (evidence_char_budget, max_output_tokens). Web-verified 2026-06-04
# against AWS official model cards + the Bedrock constraint
# `input_tokens + max_tokens <= context_window` (LiteLLM PR #22479).
# Per-family published Bedrock caps:
#   Sonnet 4.6: ctx 1,000,000  max_output 8,192   (Anthropic spec)
#   Kimi K2.5 : ctx   262,144  max_output 16,384  (AWS card)
#   GLM 5     : ctx   202,752  max_output 16,384  (AWS card lists 128K, capped at 16K — verdicts never need more)
# Budget formula: budget_chars = (ctx − max_output − 3000_safety) × cpt_floor,
# then floor to nearest 25k. Honoring the AWS-published max_output (not a single
# global 4K) is what makes the math fit, because Bedrock enforces
# input + max <= ctx so the budget MUST account for the actual maxTokens sent.
# Conservative cpt floors measured on dense fixtures (amanda_hayes_01 run_3,
# which 400'd at the old over-wide budgets): Sonnet 1.375, Kimi/GLM 1.15.
#   Sonnet: (1,000,000 − 8192 − 3000) × 1.375 − 5000 scaffold → 1_350_000
#   Kimi  : (262,144 − 16,384 − 3000) × 1.15  − 5000 scaffold → 225_000
#   GLM   : (202,752 − 16,384 − 3000) × 1.15  − 5000 scaffold → 175_000
# Don't widen without re-running probe_judge_only.py against a representative
# trajectory; tests/test_judge_budget_invariant.py guards the worst-case math.
_FAMILY_EVIDENCE: dict[str, tuple[int, int]] = {
    "sonnet": (1_350_000, 8192),
    "kimi": (225_000, 16384),
    "glm": (175_000, 16384),
}
# Anthropic prompt-caching eligibility by family. Only Sonnet (Anthropic) accepts
# a cachePoint block on Bedrock Converse; GLM/Kimi return 403 if one is present.
_FAMILY_CACHE_SUPPORTED: dict[str, bool] = {
    "sonnet": True,
    "glm": False,
    "kimi": False,
}

# OpenAI single-judge fallback rates, keyed by model NAME (NOT a council family,
# never rotated). Used when family is None (gpt-5.4 default fallback, gpt-5.5).
_OPENAI_JUDGE_RATES: dict[str, tuple[float, float, float, float]] = {
    "gpt-5.4": (2.5e-6, 1.5e-5, 2.5e-7, 0.0),
    "gpt-5.5": (5e-6, 3e-5, 5e-7, 0.0),
}


@dataclass(frozen=True)
class CouncilMember:
    """A council judge: stable `family` label + its current (rotating) `model` ARN."""

    family: JudgeFamily
    model: str


def _family_for(model: str | None, family: str | None = None) -> str | None:
    # Threaded family wins; else dispatch by the FIXED env-var name (read live).
    # None => non-council (OpenAI fallback), caller uses name-keyed _OPENAI_JUDGE_RATES.
    if family is not None:
        return family
    if not model:
        return None
    for fam, var in _FAMILY_ENV_VARS:
        val = (os.environ.get(var) or "").strip()
        if val and (val == model or val in model or model in val):
            return fam
    return None


def _member_evidence_budget(model: str, family: str | None = None) -> int | None:
    env_raw = os.environ.get("JUDGE_MAX_EVIDENCE")
    if env_raw is not None and env_raw.strip() != "":
        return _resolve_judge_max_evidence()
    fam = _family_for(model, family)
    if fam is not None and fam in _FAMILY_EVIDENCE:
        base = min(_FAMILY_EVIDENCE[fam][0], _AWS_EDGE_BODY_CAP)
        if fam == "sonnet":
            try:
                from . import judge_litellm

                if judge_litellm._judge_oauth_bridge_url():
                    return min(base, _judge_oauth_max_evidence())
            except Exception:
                pass
        return base
    return _DEFAULT_JUDGE_MAX_EVIDENCE


def _member_max_output_tokens(arn: str, family: str | None = None) -> int:
    fam = _family_for(arn, family)
    if fam is not None and fam in _FAMILY_EVIDENCE:
        return _FAMILY_EVIDENCE[fam][1]
    return _DEFAULT_MAX_OUTPUT_TOKENS

# LLM council (opt-in). When enabled the rubric is scored by THREE judges in
# parallel. Per-criterion aggregation is unanimous-or-Sonnet-tiebreak: a unanimous
# council verdict stands, otherwise the Sonnet member's verdict is the source of
# truth (covering both genuine Yes/No splits and partial coverage where a
# smaller-context member truncated), and only when Sonnet casts no verdict does
# the criterion route to Human Evaluation (see _grade_council). Each member's
# family is fixed by the env-var NAME carrying its ARN (see the FAMILY block
# above); the rotating ARN itself comes from .env, never hardcoded:
#   JUDGE_COUNCIL=1
#   JUDGE_COUNCIL_SONNET_ARN=bedrock/<arn>   (→ family "sonnet")
#   JUDGE_COUNCIL_GLM_ARN=bedrock/<arn>      (→ family "glm")
#   JUDGE_COUNCIL_KIMI_ARN=bedrock/<arn>     (→ family "kimi")
# Override roster with JUDGE_COUNCIL_MEMBERS using "family=arn" tag syntax:
#   JUDGE_COUNCIL_MEMBERS=sonnet=bedrock/<arn1>,glm=bedrock/<arn2>,kimi=bedrock/<arn3>
# Unset per-family vars are dropped; an unknown family tag RAISES (fail-fast,
# symmetric with validate_judge_pricing). Vars are read LIVE per call (no
# import-time caching) so a mid-process rotation is picked up immediately.


def council_enabled() -> bool:
    return os.environ.get("JUDGE_COUNCIL", "").strip() in {"1", "true", "yes", "on"}


def _parse_council_member_override(entry: str) -> CouncilMember:
    """Parse one JUDGE_COUNCIL_MEMBERS CSV entry in "family=arn" tag syntax."""
    raw = entry.strip()
    fam, sep, arn = raw.partition("=")
    fam = fam.strip().lower()
    arn = arn.strip()
    if not sep or not fam or not arn:
        raise RuntimeError(
            f"JUDGE_COUNCIL_MEMBERS entry {entry!r} must use 'family=arn' syntax "
            f"(e.g. 'sonnet=bedrock/arn:...'); known families: {sorted(_KNOWN_FAMILIES)}."
        )
    if fam not in _KNOWN_FAMILIES:
        raise RuntimeError(
            f"JUDGE_COUNCIL_MEMBERS entry {entry!r} has unknown family {fam!r}; "
            f"known families: {sorted(_KNOWN_FAMILIES)}."
        )
    return CouncilMember(family=fam, model=arn)  # type: ignore[arg-type]


def council_members() -> list[CouncilMember]:
    """Resolve the council roster as (family, ARN) pairs, reading env LIVE.

    Precedence: JUDGE_COUNCIL_MEMBERS ("family=arn" CSV) overrides the per-family
    JUDGE_COUNCIL_{SONNET,GLM,KIMI}_ARN vars. Unset per-family vars are dropped.
    """
    raw = os.environ.get("JUDGE_COUNCIL_MEMBERS", "").strip()
    if raw:
        return [_parse_council_member_override(m) for m in raw.split(",") if m.strip()]
    out: list[CouncilMember] = []
    for fam, var in _FAMILY_ENV_VARS:
        val = (os.environ.get(var) or "").strip()
        if val:
            out.append(CouncilMember(family=fam, model=val))  # type: ignore[arg-type]
    return out


def _judge_system_prompt() -> str:
    # 2026-06-02 judge rewrite — the prompt body lives in
    # system_prompts/judge_system.md (b78 walkthrough_2026_05_27 spec, b96
    # centralization). It encodes four operationally-essential rules whose
    # absence produces graders that drift: the EXACT verdict format the
    # parser regex depends on (deviation → ParseError → council quorum
    # collapse), truncation handling (do not penalize beyond visible
    # evidence), negative-rubric polarity (Satisfied=Yes means the forbidden
    # behavior OCCURRED, not that the guardrail held), and the Yes/No-only
    # emission (no N/A, no Maybe, no markdown tables). All four are
    # referenced in the matching parser at _VERDICT_RE and in the aggregator
    # at _grade_council; changing the prompt without updating both is a
    # known-bad refactor pattern.
    from src.utils.prompt_loader import load_prompt
    return load_prompt("judge_system")


# Rubric schemas in this repo store the weight under either `weight` or
# `score` (kensei2-style rubrics use `score`, with the SIGN encoding polarity
# — negative for guardrail / forbidden-behavior criteria). The judge prompt's
# polarity semantics live entirely in the weight sign, so missing this fallback
# silently flattens all guardrail criteria to positive weight=1.0 and inverts
# the pass-count for any criterion the agent CORRECTLY refrained from.
def _extract_weight(r: dict) -> float:
    w = r.get("weight")
    if w is None:
        w = r.get("score")
    if w is None:
        return 1.0
    try:
        return float(w)
    except (TypeError, ValueError):
        return 1.0


def _split_evidence(evidence: str) -> tuple[str, str]:
    marker = "\n----- TRANSCRIPT (condensed) -----\n"
    if marker in evidence:
        files_part, _, transcript_part = evidence.partition(marker)
        return files_part, transcript_part
    return evidence, ""


def _judge_user_prompt(task_description: str, rubrics: list, evidence: str) -> str:
    from src.utils.prompt_loader import load_prompt
    output_files, transcript = _split_evidence(evidence)
    crit_lines = []
    for i, r in enumerate(rubrics):
        crit = r.get("criterion") if isinstance(r, dict) else str(r)
        wt = _extract_weight(r) if isinstance(r, dict) else 1.0
        crit_lines.append(f"{i + 1}. {crit}  [points: {wt}]")
    return load_prompt(
        "judge_user",
        task_description=task_description,
        transcript=transcript or "(no transcript captured)",
        output_files=output_files or "(no deliverable files were collected)",
        rubrics_block="\n".join(crit_lines),
        n_criteria=len(rubrics),
    )


# Per real-task forensics, agents intuit several different deliverable-root
# names (results, deliverables, output, out, artifacts). Hard-coding only
# results/ silently zeros out otherwise-correct runs (see Claude run in the
# trajectory failure report — wrote to deliverables/, scored 0/18).
_DELIVERABLE_DIR_NAMES = ("results", "deliverables", "output", "out", "artifacts")

# Text-readable deliverable formats. Files matching these go straight into the
# judge evidence dump unmodified (UTF-8 read, errors='replace'). Adding a
# binary extension here regresses per-member evidence parity: a 512 KB PDF
# becomes ~512 KB of mojibake which sorts ahead of report.md and exhausts the
# smaller council members' (Kimi 225 KB, GLM 175 KB per _FAMILY_EVIDENCE)
# truncation budget, producing "no report.md found" hallucinations. Strictly
# text-only here.
_DELIVERABLE_EXTS = {
    ".csv", ".tsv", ".md", ".markdown", ".json", ".txt", ".text",
    ".yaml", ".yml", ".html", ".htm", ".xml", ".log",
}
# Binary deliverable formats. These are made VISIBLE to the grader (listed in
# the deliverables manifest, collected by `_collect_deliverable_files`) so
# rubrics that simply check "did the agent produce report.pdf?" can grade them,
# but their content does NOT go into the judge evidence dump verbatim — the
# mojibake-poisoning hazard above still applies. A host-side text-extraction
# pass (pypdf / openpyxl / python-docx / python-pptx) will be wired into
# `_is_text_deliverable` in a follow-up step; until then binaries appear as
# presence-only entries.
_BINARY_DELIVERABLE_EXTS = {
    ".pdf", ".xlsx", ".docx", ".pptx",
}
_ALL_DELIVERABLE_EXTS = _DELIVERABLE_EXTS | _BINARY_DELIVERABLE_EXTS
_ROOT_SCAN_MAX_FILE_BYTES = 512_000   # skip oversized files in the root scan


def _looks_like_deliverable(path: Path, root: Path) -> bool:
    """True if a workspace-root file looks like agent output (any deliverable
    extension, text or supported binary) rather than an oversized blob or binary
    input outside our supported set. Used by the presence-scan stage so binaries
    like report.pdf / flagged_items.xlsx surface in the manifest."""
    if path.suffix.lower() not in _ALL_DELIVERABLE_EXTS:
        return False
    try:
        return path.stat().st_size <= _ROOT_SCAN_MAX_FILE_BYTES
    except OSError:
        return False


def _is_text_deliverable(path: Path) -> bool:
    # Binary artifacts (.jpg/.pdf/.png) read with errors='replace' inject
    # hundreds of KB of mojibake that sorts ahead of report.md and exhausts the
    # smaller council members' truncation budget, breaking per-member evidence
    # parity (Kimi/GLM hallucinating 'no report.md'). Text-only here. Supported
    # binaries (_BINARY_DELIVERABLE_EXTS) flow through _looks_like_deliverable
    # for presence, but are excluded from this verbatim-content path until
    # host-side text extraction lands.
    return path.suffix.lower() in _DELIVERABLE_EXTS


def _is_binary_deliverable(path: Path) -> bool:
    """True if the path is a recognised binary deliverable (pdf/xlsx/docx/pptx)
    whose content we cannot dump verbatim into judge evidence today, but whose
    presence still must appear in the manifest for rubrics keyed on file
    existence (e.g. 'did the agent write report.pdf?')."""
    return path.suffix.lower() in _BINARY_DELIVERABLE_EXTS


def _collect_deliverable_files(workspace_results: Path) -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()

    def _add_from(root: Path) -> None:
        if not root.is_dir():
            return
        for f in sorted(root.rglob("*")):
            if not (f.is_file() and f not in seen):
                continue
            if _is_text_deliverable(f):
                seen.add(f)
                files.append(f)
            elif _is_binary_deliverable(f):
                try:
                    if f.stat().st_size <= _ROOT_SCAN_MAX_FILE_BYTES:
                        seen.add(f)
                        files.append(f)
                except OSError:
                    continue

    if workspace_results:
        results_path = Path(workspace_results)
        _add_from(results_path)
        # Sibling sweep: workspace_full/<deliverable-name>/ written by the agent
        # outside results/ — collect_output_from_container always preserves the
        # full /tmp_workspace tree under workspace_full/ for exactly this case.
        workspace_root = results_path.parent.parent if results_path.name == "results" else results_path.parent
        for sibling in (workspace_root / "workspace_full", workspace_root):
            if not sibling.is_dir():
                continue
            for name in _DELIVERABLE_DIR_NAMES:
                _add_from(sibling / name)
            # Some agents save deliverables at the workspace ROOT (e.g.
            # /tmp_workspace/foo.csv) rather than in a named subdir. Recover
            # text-like deliverable files sitting directly under the sweep root,
            # without recursing into input/scaffold subtrees.
            for f in sorted(sibling.glob("*")):
                if f.is_file() and f not in seen and _looks_like_deliverable(f, sibling):
                    seen.add(f)
                    files.append(f)
    return files


def _gather_evidence(
    workspace_results: Path,
    transcript_text: str,
    budget: int | None = None,
) -> str:
    parts: list[str] = []
    deliverables = _collect_deliverable_files(workspace_results)
    # Order so primary outputs survive every member's truncation budget: named
    # report/flagged deliverables first, then ascending file size (small,
    # high-signal text before bulky dumps). Without this, alphabetical order can
    # bury report.md behind larger files for the smaller-context judges.
    _PRIMARY = ("report", "flagged")

    def _priority(path: Path) -> tuple:
        stem = path.stem.lower()
        rank = 0 if any(k in stem for k in _PRIMARY) else 1
        try:
            size = path.stat().st_size
        except OSError:
            size = 1 << 30
        return (rank, size, path.name)

    for f in sorted(deliverables, key=_priority):
        try:
            body = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        parts.append(f"\n----- DELIVERABLE: {f.name} -----\n{body}")
    if not parts:
        parts.append(
            "\n(no deliverable files were collected under any of: "
            + ", ".join(f"{n}/" for n in _DELIVERABLE_DIR_NAMES)
            + ")\n"
        )
    if transcript_text:
        parts.append(f"\n----- TRANSCRIPT (condensed) -----\n{transcript_text}")
    blob = "".join(parts)
    effective = _JUDGE_MAX_EVIDENCE if budget is None else budget
    return blob if effective is None else blob[:effective]


_ZERO_USAGE = {
    "input_tokens": 0,
    "output_tokens": 0,
    "cache_read_tokens": 0,
    "cache_write_tokens": 0,
    "total_tokens": 0,
    "request_count": 0,
    "cost_usd": 0.0,
}


# Judge per-token rate resolution. Council members resolve via their stable
# FAMILY (_FAMILY_RATES, rotation-proof); OpenAI single-judge fallbacks resolve
# by model NAME (_OPENAI_JUDGE_RATES). Both tables live in the FAMILY block above
# and MUST track real published provider list prices — the council cost line in
# usage.json is computed directly from them (NOT via litellm), so any drift
# silently mis-bills every graded task. There is no longer a profile-id-keyed
# rate table: a rotating id is never a billing key.
def _judge_rate_for(
    model: str, family: str | None = None
) -> tuple[float, float, float, float] | None:
    fam = _family_for(model, family)
    if fam is not None:
        return _FAMILY_RATES.get(fam)
    # Non-council (OpenAI) judge: substring-match the model name.
    for key, val in _OPENAI_JUDGE_RATES.items():
        if key in (model or ""):
            return val
    return None


def _judge_cost_usd(
    model: str, in_tok: int, out_tok: int, c_read: int, c_write: int,
    family: str | None = None,
) -> tuple[float, bool]:
    # Returns (cost_usd, priced_ok). An unknown model is soft-degraded to
    # (0.0, False) here rather than raising, so a long grading run never crashes
    # mid-flight on a mis-configured judge. The fail-fast guarantee lives in
    # validate_judge_pricing(), called at grade_with_rubric() startup; callers
    # that bypass grade_with_rubric must run that validator themselves first.
    # Subscription judging (sonnet via the Claude Max OAuth bridge) is not
    # metered per-token — it draws on the flat Max plan — so the per-token list
    # price would be a misleading "charge". Force cost_usd=0 (priced_ok=True) for
    # that path; real cost is reconciled separately later. Token counts are kept.
    if family == "sonnet":
        try:
            from . import judge_litellm  # local import: avoid import-time cost
            if judge_litellm._judge_oauth_bridge_url():
                return 0.0, True
        except Exception:
            pass
    rate = _judge_rate_for(model, family)
    if rate is None:
        logger.error(
            "[judge_cost] no rate for judge model=%r family=%r; cost recorded as "
            "0.0 and flagged unpriced. Add a council family to _FAMILY_RATES or an "
            "OpenAI model to _OPENAI_JUDGE_RATES in grading.py.",
            model, family,
        )
        return 0.0, False
    r_in, r_out, r_cached, r_cwrite = rate
    cost = in_tok * r_in + c_read * r_cached + c_write * r_cwrite + out_tok * r_out
    return cost, True


def validate_judge_pricing(members: Sequence[CouncilMember | str]) -> None:
    # Fail-fast at config boundary (grade_with_rubric startup), never mid-run.
    # Two distinct failure modes so the operator knows which table to edit:
    # a CouncilMember with an unpriced family vs an OpenAI judge name with no rate.
    bad_family: list[str] = []
    bad_openai: list[str] = []
    for m in members:
        if isinstance(m, CouncilMember):
            if m.family not in _FAMILY_RATES:
                bad_family.append(f"{m.family} ({m.model})")
        elif _judge_rate_for(m) is None:
            bad_openai.append(m)
    if bad_family:
        raise RuntimeError(
            "Council member(s) have no _FAMILY_RATES entry and would be billed at "
            f"$0: {bad_family}. Add the family's per-token rates before running."
        )
    if bad_openai:
        raise RuntimeError(
            "OpenAI judge model(s) have no _OPENAI_JUDGE_RATES entry and would be "
            f"billed at $0: {bad_openai}. Add per-token rates before running."
        )


def _call_judge_openai(model: str, system: str, user: str) -> tuple[str, dict]:
    import urllib.request
    key = os.environ.get("KENSEI_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY", "")
    if not key:
        raise RuntimeError("no OpenAI key for judge")
    # Yes/No verdict format (judge_walkthrough_2026_05_27.html §1.1 EXACT FORMAT):
    # judge emits free-form text with `[[RATIONALE:]] [[SATISFIED:Yes|No]]` blocks
    # wrapped in `<judgment>...</judgment>`. We MUST NOT pass
    # `response_format={"type":"json_object"}` here — it forces OpenAI to wrap
    # the entire response in a JSON envelope, which breaks `_VERDICT_RE` and
    # collapses every council vote into a parse error. max_completion_tokens
    # raised 4000→8000 so 25-criterion rubrics (≈1.2k verdict tokens) leave
    # ample headroom for reasoning.
    body = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "max_completion_tokens": 8000,
        "stream": True,
        "stream_options": {"include_usage": True},
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions", data=body, method="POST",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "Accept": "text/event-stream"},
    )
    text_parts: list[str] = []
    u: dict = {}
    # Live-stream tap (docs/STREAMING_PLAN.md §3.3), same pattern as the
    # Bedrock judge path: emit each delta as it accumulates; no-op when
    # WCB_STREAM is off; never raises.
    from src.utils import stream_events as _stream
    import uuid as _uuid
    _sid = _uuid.uuid4().hex[:12]
    _stream.emit("judge:openai", "message_start", _sid, kind="status", model=model)
    with urllib.request.urlopen(req, timeout=120) as r:
        for raw_line in r:
            line = raw_line.decode("utf-8", errors="replace").rstrip("\r\n")
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if payload == "[DONE]":
                break
            try:
                obj = json.loads(payload)
            except json.JSONDecodeError:
                continue
            choices = obj.get("choices") or []
            if choices:
                delta = choices[0].get("delta") or {}
                content = delta.get("content")
                if isinstance(content, str):
                    text_parts.append(content)
                    _stream.emit("judge:openai", "delta", _sid, kind="text",
                                 delta=content, model=model)
            usage_obj = obj.get("usage")
            if isinstance(usage_obj, dict):
                u = usage_obj
    _stream.emit("judge:openai", "message_stop", _sid, kind="status", model=model)
    text = "".join(text_parts)
    details = u.get("prompt_tokens_details", {}) or {}
    prompt_tok = int(u.get("prompt_tokens", 0) or 0)
    comp_tok = int(u.get("completion_tokens", 0) or 0)
    cached_tok = int(details.get("cached_tokens", 0) or 0)
    input_excl = max(0, prompt_tok - cached_tok)
    cost_usd, priced_ok = _judge_cost_usd(model, input_excl, comp_tok, cached_tok, 0)
    usage = {
        "input_tokens": input_excl,
        "output_tokens": comp_tok,
        "cache_read_tokens": cached_tok,
        "cache_write_tokens": 0,
        "total_tokens": input_excl + comp_tok + cached_tok,
        "request_count": 1,
        "cost_usd": cost_usd,
        "cost_priced_ok": priced_ok,
    }
    return text, usage


_ARN_REGION_RE = re.compile(r"^arn:aws:bedrock:([a-z0-9-]+):")

# Bedrock prompt-caching support is per-model. Anthropic Claude on Bedrock
# accepts `cachePoint` blocks; Kimi and GLM do NOT and return HTTP 403 "You
# invoked an unsupported model or your request did not allow prompt caching."
# Observed in alden-croft 2026-06-02T20:20:04Z gateway.log: 2-of-3 council
# members 403'd, quorum fell back to single-judge.
#
# TWO LAYERS, because a council member's id rotates monthly but a direct-ARN
# (non-council) judge does not:
#   Layer 1 — council members resolve by stable FAMILY (_FAMILY_CACHE_SUPPORTED),
#             so caching eligibility survives ARN rotation.
#   Layer 2 — non-council / direct-ARN paths (single-judge fallback, future
#             judges) fall back to this substring allowlist of profile IDs known
#             to map to Anthropic Claude. These are NOT council ids and are not
#             rotated. Add a new ID only after confirming the model is Anthropic.
_NON_COUNCIL_CACHE_SUPPORTED_TAILS = (
    "xv71vnlzm71s",  # Sonnet 4.6 (alternate; IAM-denied per b34 but caches when permitted)
    "96j5zamnqlci",  # Opus (.env KENSEI_BEDROCK_MODEL_ARN)
)


def _supports_prompt_caching(arn: str, family: str | None = None) -> bool:
    if family is not None:
        return _FAMILY_CACHE_SUPPORTED.get(family, False)
    return any(tail in (arn or "") for tail in _NON_COUNCIL_CACHE_SUPPORTED_TAILS)


def _bedrock_region_for(arn: str) -> str:
    m = _ARN_REGION_RE.match(arn or "")
    if m:
        return m.group(1)
    return os.environ.get("KENSEI_AWS_REGION") or os.environ.get("AWS_REGION", "ap-south-1")


def _call_judge_bedrock(
    arn: str, system: str, user: str, family: str | None = None
) -> tuple[str, dict]:
    import urllib.request, urllib.parse, urllib.error
    from src.utils.bedrock_eventstream import iter_eventstream
    tok = os.environ.get("KENSEI_AWS_BEARER_TOKEN") or os.environ.get("AWS_BEARER_TOKEN_BEDROCK", "")
    if not tok:
        raise RuntimeError("no Bedrock bearer token for judge")
    while arn.startswith("bedrock/"):
        arn = arn[len("bedrock/"):]
    reg = _bedrock_region_for(arn)
    mid = urllib.parse.quote(arn, safe="")
    url = f"https://bedrock-runtime.{reg}.amazonaws.com/model/{mid}/converse-stream"

    def _do_post(include_temperature: bool) -> tuple[str, dict]:
        infer = {"maxTokens": _member_max_output_tokens(arn, family)}
        if include_temperature:
            infer["temperature"] = 0
        # Bedrock prompt-caching: a `cachePoint` block marks the preceding
        # blocks as cacheable for ~5 min on Anthropic models. Kimi K2.5 and
        # GLM 5 on Bedrock return 403 "your request did not allow prompt
        # caching" if cachePoint is present (see _CACHE_SUPPORTED_PROFILE_IDS
        # above). Gate emission on per-ARN allowlist; preserve b49 caching
        # win on Sonnet/Opus without re-triggering the 2-of-3 council quorum
        # collapse observed in alden-croft 2026-06-02T20:20Z gateway.log.
        if _supports_prompt_caching(arn, family):
            system_blocks = [{"text": system}, {"cachePoint": {"type": "default"}}]
        else:
            system_blocks = [{"text": system}]
        body = json.dumps({
            "system": system_blocks,
            "messages": [{"role": "user", "content": [{"text": user}]}],
            "inferenceConfig": infer,
        }).encode()
        req = urllib.request.Request(
            url, data=body, method="POST",
            headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json",
                     "Accept": "application/vnd.amazon.eventstream"},
        )
        return _consume(req)

    def _consume(req) -> tuple[str, dict]:
        text_parts: list[str] = []
        u: dict = {}
        # Live-stream tap (docs/STREAMING_PLAN.md §3.3): each delta is emitted
        # to the display feed AS it is accumulated — accumulate-then-parse is
        # untouched (R4), and stream_events.emit() is a guaranteed no-raise
        # no-op unless WCB_STREAM is on.
        from src.utils import stream_events as _stream
        import uuid as _uuid
        _sid = _uuid.uuid4().hex[:12]
        _src = f"judge:{family or 'bedrock'}"
        try:
            resp = urllib.request.urlopen(req, timeout=120)
        except urllib.error.HTTPError as e:
            err_body = ""
            try:
                err_body = e.read().decode("utf-8", "replace")[:2000]
            except Exception:
                pass
            _stream.emit(_src, "error", _sid, kind="status",
                         delta=f"HTTP {e.code}", model=arn)
            raise RuntimeError(f"Bedrock HTTP {e.code} at {url}: {err_body}") from None
        _stream.emit(_src, "message_start", _sid, kind="status", model=arn)
        with resp as r:
            def _chunks():
                while True:
                    chunk = r.read(8192)
                    if not chunk:
                        return
                    yield chunk
            for evt_type, evt_payload in iter_eventstream(_chunks()):
                if not isinstance(evt_payload, dict):
                    continue
                if evt_type and evt_type.endswith("Exception"):
                    err = evt_payload.get("Message") or evt_payload.get("message") or ""
                    _stream.emit(_src, "error", _sid, kind="status",
                                 delta=str(err)[:200], model=arn)
                    raise RuntimeError(f"Bedrock judge error ({evt_type}): {err}")
                if evt_type == "contentBlockDelta":
                    delta = evt_payload.get("delta") or {}
                    txt = delta.get("text")
                    if isinstance(txt, str):
                        text_parts.append(txt)
                        _stream.emit(_src, "delta", _sid, kind="text",
                                     delta=txt, model=arn)
                elif evt_type == "metadata":
                    usage_obj = evt_payload.get("usage")
                    if isinstance(usage_obj, dict):
                        u = usage_obj
        _stream.emit(_src, "message_stop", _sid, kind="status", model=arn)
        text = "".join(text_parts)
        in_tok = int(u.get("inputTokens", 0) or 0)
        out_tok = int(u.get("outputTokens", 0) or 0)
        c_read = int(
            u.get("cacheReadInputTokens")
            or u.get("cacheReadTokens")
            or u.get("cache_read_input_tokens")
            or 0
        )
        c_write = int(
            u.get("cacheWriteInputTokens")
            or u.get("cacheCreationInputTokens")
            or u.get("cache_creation_input_tokens")
            or 0
        )
        cost_usd, priced_ok = _judge_cost_usd(arn, in_tok, out_tok, c_read, c_write, family)
        usage = {
            "input_tokens": in_tok,
            "output_tokens": out_tok,
            "cache_read_tokens": c_read,
            "cache_write_tokens": c_write,
            "total_tokens": in_tok + out_tok + c_read + c_write,
            "request_count": 1,
            "cost_usd": cost_usd,
            "cost_priced_ok": priced_ok,
        }
        return text, usage

    try:
        return _do_post(include_temperature=True)
    except RuntimeError as exc:
        msg = str(exc).lower()
        if "temperature" in msg and ("deprecated" in msg or "not supported" in msg or "unsupported" in msg):
            return _do_post(include_temperature=False)
        raise


# Parser for the Yes/No verdict format mandated by _judge_system_prompt. Three
# load-bearing properties: (1) DOTALL so rationale text can span newlines,
# (2) the leading 'N.' anchor disambiguates each verdict block when judges
# emit Markdown-style bold/italic markers around the criterion sentence,
# (3) TRUNCATION_AFFECTED is OPTIONAL so a judge that omits it (older models,
# rare miss-emission) does not collapse the whole verdict count and trigger
# quorum failure. Defaults to No when absent. Match this regex's structure
# against any change to the system prompt's verdict template; deviation here
# silently zeros all judge votes — see 2026-06-02 alden-croft regression
# context referenced in _judge_system_prompt.
_VERDICT_RE = re.compile(
    r"\d+\.\s.*?"
    r"\[\[\s*RATIONALE:\s*(.*?)\s*\]\]\s*"
    r"\[\[\s*SATISFIED:\s*(Yes|No)\s*\]\]"
    r"(?:\s*\[\[\s*TRUNCATION_AFFECTED:\s*(Yes|No)\s*\]\])?",
    re.DOTALL | re.IGNORECASE,
)


def _parse_verdict_text(response: str, n_criteria: int) -> list[dict]:
    if not response:
        raise ValueError(f"empty judge response (expected up to {n_criteria} verdicts)")
    # Tolerate judges that wrap the entire block in <judgment>...</judgment> or
    # emit it bare; either way the verdict items themselves are what we match.
    matches = _VERDICT_RE.findall(response)
    # Partial-coverage contract per user m1543: smaller-context judges
    # (Kimi K2.5 = 256k input, GLM 5 = 200k input) truncate output before
    # reaching all rubric items on long rubrics (Sonnet 4.6 = 1M handles 69+
    # comfortably). Renata-voss 2026-06-03 produced GLM=59 / Kimi=54 / Sonnet=69
    # for a 69-criterion rubric. Returning the partial list lets the council
    # aggregator vote per-criterion using only judges that actually covered
    # that index; abstentions never invent No-votes the model did not cast.
    if not matches:
        raise ValueError(
            f"no verdicts parsed (expected up to {n_criteria}); response shape does not match _VERDICT_RE"
        )
    out: list[dict] = []
    # Cap at n_criteria in case a judge emits stray numbered items beyond the
    # rubric (defensive — verdict list is ordered, criteria N+1.. would be junk).
    for rationale, satisfied, truncation in matches[:n_criteria]:
        out.append({
            "rationale": (rationale or "").strip(),
            "satisfied": (satisfied or "No").strip().lower() == "yes",
            "truncation_affected": (truncation or "No").strip().lower() == "yes",
        })
    return out


def _arn_from_model(model: str) -> str:
    """Strip the optional 'bedrock/' prefix so `_member_max_output_tokens` and
    `_bedrock_region_for` (which do substring matches against ARN tails) work
    identically whether the caller passed `bedrock/arn:...` or the bare ARN.
    Non-Bedrock model strings pass through unchanged."""
    m = (model or "").strip()
    if m.startswith("bedrock/"):
        return m[len("bedrock/"):]
    return m


def _judge_use_litellm() -> bool:
    """Master toggle for the LiteLLM-backed judge path. Mirrors
    `judge_litellm.judge_use_litellm()` but is duplicated here so the env check
    is a cheap module-local function call — we don't want to import the
    `judge_litellm` module on every judge call when the flag is off. Default
    OFF: the urllib direct-provider path is the production-verified default;
    flipping to LiteLLM is opt-in until soak validates the new transport."""
    v = os.environ.get("KENSEI_JUDGE_USE_LITELLM", "").strip().lower()
    return v in ("1", "true", "yes", "on")


def _call_one_judge(
    model: str, system: str, user: str, family: str | None = None
) -> tuple[str, dict]:
    # Provider routing is CONTENT-AWARE, not naive partition("/"): a Bedrock
    # application-inference-profile ARN itself contains slashes, so a bare ARN
    # (missing the "bedrock/" prefix) would partition to provider != "bedrock" and
    # be silently misrouted to OpenAI, which 404s on the unknown model id. Detect
    # Bedrock by shape so an ARN never reaches OpenAI. `family` (when the caller is
    # the council) carries the stable model identity so pricing/budget/cache
    # lookups never depend on the monthly-rotating ARN profile id.
    m = (model or "").strip()
    if not m:
        raise RuntimeError("empty judge model id")

    # LiteLLM-backed path (opt-in via KENSEI_JUDGE_USE_LITELLM). On ANY exception
    # we fall through to the urllib direct-provider path below — this is the
    # explicit user m0039 contract: "If litellm is not configured for LLM
    # council account for that as well in your plan and it should follow the
    # code at all times." A hard fallback at the dispatcher (not inside the
    # LiteLLM call) means a missing dep, a misconfigured env, a network blip,
    # or a LiteLLM-internal regression all degrade gracefully to the production
    # path without losing the verdict.
    if _judge_use_litellm():
        try:
            from . import judge_litellm  # local import: avoid import-time cost
            arn_tail = _arn_from_model(m)
            return judge_litellm.call_judge_via_litellm(
                model=m,
                system=system,
                user=user,
                max_output_tokens=_member_max_output_tokens(arn_tail, family),
                cost_fn=_judge_cost_usd,
                family=family,
            )
        except Exception as exc:  # pragma: no cover - fallback path
            logger.warning(
                "Judge LiteLLM path failed for %s: %s — falling back to direct urllib path",
                _short_judge_label(m), str(exc)[:200],
            )
            # fall through to urllib routing below

    head = m.partition("/")[0]
    if head == "bedrock":
        return _call_judge_bedrock(m.partition("/")[2], system, user, family)
    if head == "openai":
        return _call_judge_openai(m.partition("/")[2] or m, system, user)
    if m.startswith("arn:aws:bedrock:") or ":application-inference-profile/" in m:
        # Bare (unprefixed) Bedrock ARN — route to Bedrock instead of OpenAI.
        return _call_judge_bedrock(m, system, user, family)
    # Unknown/unprefixed id: treat as an OpenAI model name (e.g. "gpt-5.5").
    return _call_judge_openai(m, system, user)


def _run_council(
    members: list[CouncilMember],
    system: str,
    user_for_member: "dict[str, str] | str",
    n_criteria: int,
) -> list[dict]:
    """Run every member judge in parallel and return one result dict per member:
    {model, family, ok, verdicts?, usage, error?, user_chars, raw_response?}.
    Never raises.

    `user_for_member` may be a single shared string (legacy) or a
    {model: user_prompt} dict so each member receives a payload sized to its
    own context window. `n_criteria` is the expected verdict count; parses
    failing this count return `ok=False, error='parse: ...'` rather than raise.
    Every result carries the member's stable `family` so downstream per-member
    dicts key by family, not by the monthly-rotating ARN profile id."""
    from concurrent.futures import ThreadPoolExecutor

    def _resolve_user(model: str) -> str:
        if isinstance(user_for_member, dict):
            return user_for_member.get(model, "")
        return user_for_member

    def _one(member: CouncilMember) -> dict:
        import time as _time
        model = member.model
        family = member.family
        effective_model = _effective_judge_model(model, family)
        user = _resolve_user(model)
        label = _short_judge_label(model)
        # Per-member API call telemetry: pre-call line lets operators see WHICH
        # member is being dispatched WHAT payload before any network I/O; the
        # post-call ok/fail line below carries timing + tokens + cache deltas
        # so a single grep over `Judge call` reproduces the full council
        # fan-out from run.sh logs alone. Mirrors run_batch.py:707
        # `Rubric judged:` summary line one level up.
        logger.info(
            "Judge call start: model=%s family=%s user_chars=%d system_chars=%d",
            label, family, len(user), len(system),
        )
        t0 = _time.monotonic()
        try:
            raw, usage = _call_one_judge(model, system, user, family)
        except Exception as exc:
            elapsed = _time.monotonic() - t0
            logger.warning(
                "Judge call fail: model=%s family=%s elapsed=%.2fs stage=call error=%s",
                label, family, elapsed, str(exc)[:200],
            )
            return {
                "model": model, "effective_model": effective_model,
                "family": family, "ok": False,
                "error": f"call: {exc}",
                "usage": {**_ZERO_USAGE, "error": f"call: {exc}"},
                "user_chars": len(user),
            }
        elapsed = _time.monotonic() - t0
        in_tok = int(usage.get("input_tokens", 0) or 0)
        out_tok = int(usage.get("output_tokens", 0) or 0)
        c_read = int(usage.get("cache_read_tokens", 0) or 0)
        c_write = int(usage.get("cache_write_tokens", 0) or 0)
        try:
            verdicts = _parse_verdict_text(raw, n_criteria)
        except Exception as exc:
            logger.warning(
                "Judge call fail: model=%s family=%s elapsed=%.2fs stage=parse "
                "tokens=in:%d/out:%d/cR:%d/cW:%d error=%s",
                label, family, elapsed, in_tok, out_tok, c_read, c_write, str(exc)[:200],
            )
            return {
                "model": model, "effective_model": effective_model,
                "family": family, "ok": False,
                "error": f"parse: {exc}", "usage": usage,
                "user_chars": len(user),
                "raw_response": raw[:2000] if isinstance(raw, str) else "",
            }
        logger.info(
            "Judge call ok: model=%s family=%s elapsed=%.2fs "
            "tokens=in:%d/out:%d/cR:%d/cW:%d verdicts=%d/%d",
            label, family, elapsed, in_tok, out_tok, c_read, c_write,
            len(verdicts), n_criteria,
        )
        return {
            "model": model, "effective_model": effective_model,
            "family": family, "ok": True,
            "verdicts": verdicts, "usage": usage,
            "user_chars": len(user),
        }

    with ThreadPoolExecutor(max_workers=max(1, len(members))) as pool:
        return list(pool.map(_one, members))


def _stddev(values: list[float]) -> float:
    n = len(values)
    if n < 2:
        return 0.0
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n
    return var ** 0.5


def _criterion_pass(score: float, weight: float) -> bool:
    triggered = score >= 0.5
    return (not triggered) if weight < 0 else triggered


def _criterion_pass_from_satisfied(satisfied: bool, weight: float) -> bool:
    # Walkthrough §2 polarity rule: SATISFIED reflects the literal criterion
    # text, NOT the point sign. Aggregator applies sign here.
    #  positive weight + satisfied=True  → passed (desired thing done)
    #  positive weight + satisfied=False → failed
    #  negative weight + satisfied=False → passed (guardrail held)
    #  negative weight + satisfied=True  → failed (forbidden behavior occurred)
    return (not satisfied) if weight < 0 else satisfied


def _short_judge_label(model: str) -> str:
    """Shorten 'bedrock/arn:aws:bedrock:<region>:<acct>:application-inference-profile/<id>'
    to '<id>' for compact per-criterion arrays in score.json; preserves the
    'openai/<model>' shape verbatim."""
    if model.startswith("bedrock/"):
        return model.rsplit("/", 1)[-1]
    return model


def _effective_judge_model(model: str, family: str) -> str:
    """Model actually hit on the wire, for score.json display.

    A member's configured Bedrock ARN is only a stable label: when the sonnet
    member routes through the Claude Max OAuth bridge, judge_litellm overrides
    the request model to the anthropic model and pops the Bedrock region, so
    the endpoint is anthropic — not Bedrock. Returns that effective anthropic
    id (bare, no 'anthropic/' prefix); otherwise the raw member id."""
    if family == "sonnet":
        try:
            from . import judge_litellm  # local import: avoid import-time cost
            if judge_litellm._judge_oauth_bridge_url():
                eff = judge_litellm._judge_oauth_bridge_model()
                return eff.split("/", 1)[-1] if eff.startswith("anthropic/") else eff
        except Exception:
            pass
    return model


def _grade_council(
    rubrics: list,
    system: str,
    user_for_member: "dict[str, str] | str",
    members: list[CouncilMember],
) -> dict:
    """Council aggregation — UNANIMOUS, else SONNET source-of-truth tiebreak.

    Single-judge mode was removed (m1609): the council is the only grading path.
    Per-criterion the verdict is resolved in this order:
      * Unanimous — every member voted AND all agree on SATISFIED → use that
        verdict (Pass/Fail after polarity). `resolved_by="unanimous"`.
      * Otherwise, if the Sonnet member emitted a verdict for this criterion →
        Sonnet's verdict governs. This covers BOTH a genuine Yes/No split and
        partial coverage where a smaller-context member (Kimi/GLM) truncated
        before reaching this index. `resolved_by="sonnet"`.
      * Otherwise — no unanimity AND Sonnet itself cast no verdict (Sonnet failed
        or, rarely, truncated) → "Human Evaluation": index added to
        abstention_flags, counted in criteria_abstained, contributes 0 to the
        numerator. `resolved_by="human_eval"`, `human_eval="required"`.

    A satisfied positive criterion contributes its weight to the numerator; a
    satisfied negative criterion (forbidden behavior occurred) subtracts |weight|.
    The denominator is the sum of positive weights only.

    Always returns a scores dict; on total council failure (zero surviving members
    and therefore no Sonnet verdict) every criterion abstains and overall_score is
    0.0. No single-judge fallback exists. If the roster has no sonnet-family member,
    the tiebreak is unavailable and non-unanimous criteria abstain as before."""
    results = _run_council(members, system, user_for_member, len(rubrics))
    surviving = [r for r in results if r.get("ok") and isinstance(r.get("verdicts"), list)]
    if len(surviving) < len(members):
        failed_summary = "; ".join(
            f"{_short_judge_label(r.get('model', '?'))}={(r.get('error') or 'unknown').strip()[:160]}"
            for r in results if not r.get("ok")
        ) or "(none — all members responded)"
        # Not fatal under unanimous rule: any non-surviving member just means the
        # remaining survivors must all agree for a determinate verdict. With zero
        # survivors every criterion abstains and overall_score is 0.0.
        logger.warning(
            "Judge council partial: %d/%d members succeeded; failed: %s; "
            "criteria without full coverage will require Human Evaluation",
            len(surviving), len(members), failed_summary,
        )

    verdicts_per_member: list[list[dict]] = [r["verdicts"] for r in surviving]
    n_members = len(members)
    # survivor_lookup maps a member's (rotating) ARN → its parsed verdict list.
    # Hoisted out of the per-criterion loop below (it was rebuilt once per rubric
    # item; the surviving set is constant for the whole aggregation).
    survivor_lookup = {r["model"]: vs for r, vs in zip(surviving, verdicts_per_member)}
    # Sonnet is the tiebreaker / source of truth on any non-unanimous criterion:
    # it is the largest-context (1M) and most capable council member. Located by
    # stable FAMILY, never the rotating ARN (see the FAMILY decoupling block).
    # When the roster has no sonnet member (a custom JUDGE_COUNCIL_MEMBERS roster),
    # there is no tiebreaker and non-unanimous criteria fall back to Human
    # Evaluation as before.
    sonnet_idx = next((j for j, m in enumerate(members) if m.family == "sonnet"), None)
    if sonnet_idx is None:
        logger.warning(
            "Judge council has no 'sonnet' member; non-unanimous criteria will "
            "fall back to Human Evaluation (no source-of-truth tiebreaker)."
        )

    crit_out: list[dict] = []
    truncation_flags: list[int] = []
    abstention_flags: list[int] = []
    weighted = 0.0
    passed = 0
    # Denominator is the sum of POSITIVE weights only — walkthrough §4 verbatim:
    # 'Always use sum(positive_points). Do NOT use sum(all_points) — that
    # overshoots 1 whenever penalties exist.' Mirrors test_executor._compute_reward
    # pos_total. See alden-croft 2026-06-02 (23/23 passed → overall 0.4986 was
    # bug; positive-only denom gives 0.983 correctly).
    total_w = sum(_extract_weight(r) for r in rubrics
                  if isinstance(r, dict) and _extract_weight(r) > 0) or 1.0

    for i, r in enumerate(rubrics):
        wt = _extract_weight(r) if isinstance(r, dict) else 1.0
        # Per-criterion resolution (Sonnet source-of-truth tiebreak): a criterion
        # is determined by unanimous council agreement when every member voted and
        # agreed; otherwise Sonnet's verdict governs (genuine split OR a smaller
        # member truncating before this index); only when Sonnet itself cast no
        # verdict does the criterion route to Human Evaluation.
        per_satisfied: list[bool] = []
        per_rationale: list[str] = []
        per_truncation: list[bool] = []
        per_label: list[str] = [m.family for m in members]
        per_voted: list[bool] = []

        # Build per-member vote state aligned to the full `members` list so a
        # member that failed entirely (not in `surviving`) shows up as Abstain
        # in the votes string, matching the truncated-mid-rubric semantics.
        for m in members:
            vs = survivor_lookup.get(m.model)
            if vs is None:
                per_voted.append(False)
                per_satisfied.append(False)
                per_rationale.append("(abstained — judge call failed)")
                per_truncation.append(False)
                continue
            if i < len(vs):
                v = vs[i]
                per_voted.append(True)
                per_satisfied.append(bool(v.get("satisfied", False)))
                per_rationale.append(str(v.get("rationale", "") or ""))
                per_truncation.append(bool(v.get("truncation_affected", False)))
            else:
                per_voted.append(False)
                per_satisfied.append(False)
                per_rationale.append("(abstained — output truncated before this criterion)")
                per_truncation.append(False)

        voters = sum(1 for vd in per_voted if vd)
        full_coverage = (voters == n_members)
        if full_coverage:
            yes_votes = sum(1 for s in per_satisfied if s)
            unanimous_yes = (yes_votes == n_members)
            unanimous_no = (yes_votes == 0)
        else:
            unanimous_yes = False
            unanimous_no = False

        sonnet_voted = sonnet_idx is not None and per_voted[sonnet_idx]

        # Resolution policy (Sonnet source-of-truth tiebreak):
        #   1. Unanimous — all members voted AND agree → use that verdict.
        #   2. Otherwise, if Sonnet emitted a verdict → Sonnet IS the verdict.
        #      This covers BOTH a genuine Yes/No split AND partial coverage where
        #      a smaller-context member (Kimi/GLM) truncated before this index.
        #   3. Otherwise (no unanimity AND Sonnet itself cast no verdict) →
        #      Human Evaluation (abstention): no source of truth exists.
        if full_coverage and (unanimous_yes or unanimous_no):
            verdict_satisfied = unanimous_yes
            resolved_by = "unanimous"
            human_eval = ""
        elif sonnet_voted:
            verdict_satisfied = bool(per_satisfied[sonnet_idx])
            resolved_by = "sonnet"
            human_eval = ""
        else:
            abstention_flags.append(i)
            verdict_satisfied = False
            resolved_by = "human_eval"
            human_eval = "required"

        if resolved_by == "human_eval":
            criterion_passed = False
        else:
            criterion_passed = _criterion_pass_from_satisfied(verdict_satisfied, wt)
            if criterion_passed:
                passed += 1
            # Reward (walkthrough §4): a positive-weight criterion contributes its
            # weight only when the resolved verdict is satisfied; a negative-weight
            # criterion that is satisfied (forbidden behavior occurred) subtracts
            # its |weight|. No fractions. b51 leak impossible.
            if verdict_satisfied:
                weighted += wt

        if any(per_truncation):
            truncation_flags.append(i)
        crit_out.append({
            "id": i,
            "weight": wt,
            "satisfied": verdict_satisfied,
            "passed": criterion_passed,
            "resolved_by": resolved_by,
            "human_eval": human_eval,
            "voters": voters,
            "criterion": (r.get("criterion") if isinstance(r, dict) else str(r)),
            "votes": "/".join(
                ("Yes" if s else "No") if vd else "Abstain"
                for s, vd in zip(per_satisfied, per_voted)
            ),
            "satisfied_by_judge": per_satisfied,
            "voted_by_judge": per_voted,
            "rationales_by_judge": per_rationale,
            "truncation_affected_by_judge": per_truncation,
            "judges": per_label,
            "is_positive": wt >= 0,
        })

    # User formula (verbatim, no clamp):
    #   final_reward = (Σ passed_positive_w − Σ |triggered_negative_w|) / Σ positive_w
    # Negative-weight violation checkers must be able to pull the reward below
    # zero; clamping here silently erases their signal.
    overall = weighted / total_w
    council_usage = _ZERO_USAGE.copy()
    # Per-member usage breakdown: the flat sum below collapses all members into
    # one cost line, hiding which model spent what. Preserve each member's own
    # tokens/cost keyed by stable FAMILY ('sonnet'/'glm'/'kimi'), NOT the monthly-
    # rotating ARN profile id — so a tool reading sources.judge.per_member finds
    # the same keys before and after an ARN rotation. Rides on council_usage as a
    # non-numeric passthrough, so recompute_combined leaves it alone and the
    # total=in+out+cR+cW invariant is unaffected.
    per_member: dict[str, dict] = {}
    for r in results:
        u = r.get("usage") or {}
        for k in council_usage.keys():
            if k == "cost_usd":
                council_usage[k] = float(council_usage.get(k, 0.0)) + float(u.get(k, 0.0) or 0.0)
            else:
                council_usage[k] = int(council_usage.get(k, 0)) + int(u.get(k, 0) or 0)
        in_tok = int(u.get("input_tokens", 0) or 0)
        out_tok = int(u.get("output_tokens", 0) or 0)
        cr_tok = int(u.get("cache_read_tokens", 0) or 0)
        cw_tok = int(u.get("cache_write_tokens", 0) or 0)
        # per_member.model must match judge_council.members/surviving (the
        # OAuth-bridge effective label, not the rotating Bedrock ARN).
        _member_model = r.get("effective_model") or r.get("model", "")
        member_entry: dict = {
            "model": _member_model,
            "input_tokens": in_tok,
            "output_tokens": out_tok,
            "cache_read_tokens": cr_tok,
            "cache_write_tokens": cw_tok,
            "total_tokens": in_tok + out_tok + cr_tok + cw_tok,
            "request_count": int(u.get("request_count", 0) or 0),
            "cost_usd": float(u.get("cost_usd", 0.0) or 0.0),
            "ok": bool(r.get("ok")),
        }
        if "cost_priced_ok" in u:
            member_entry["cost_priced_ok"] = bool(u.get("cost_priced_ok"))
        if r.get("error"):
            member_entry["error"] = str(r.get("error"))[:200]
        # Key by family (unique per council: one sonnet/glm/kimi each); fall
        # back to the full model string only if family is somehow absent.
        key = r.get("family") or str(r.get("model", "") or "")
        if key in per_member:
            key = str(r.get("model", "") or key)
        per_member[key] = member_entry
    council_usage["total_tokens"] = (
        council_usage["input_tokens"] + council_usage["output_tokens"]
        + council_usage["cache_read_tokens"] + council_usage["cache_write_tokens"]
    )
    council_usage["per_member"] = per_member

    headroom_per_member: dict[str, dict] = {}
    headroom_tokens_saved_total = 0
    headroom_enabled = False
    for r in results:
        h = (r.get("usage") or {}).get("headroom") or {}
        if not isinstance(h, dict) or not h:
            continue
        headroom_enabled = True
        headroom_per_member[r.get("family") or _short_judge_label(r.get("model", ""))] = h
        headroom_tokens_saved_total += int(h.get("tokens_saved", 0) or 0)

    n = len(rubrics)
    n_abstained = len(abstention_flags)
    failed = n - passed - n_abstained
    # Schema contract — score.json scores RUBRIC CRITERIA, not pytest tests.
    # Canonical keys: criteria_total/_passed/_failed/_abstained and
    # rubric_weights_percentage (= overall_score * 100, per user formula m1420).
    # criteria_total = passed + failed + abstained (b82 invariant). The deprecated
    # tests_* aliases were dropped here; the harbor pytest channel (test_result /
    # SQLite store / ctrf.json) derives its tests_* counts from criteria_* via the
    # tr_meta adapter at eval/run_batch.py:962-968, which already falls back to
    # criteria_* when no real pytest ran. See NOMENCLATURE.md for the channel boundary.
    return {
        "overall_score": round(overall, 4),
        "rubric_weights_percentage": round(overall * 100.0, 2),
        "criteria_total": n,
        "criteria_passed": passed,
        "criteria_failed": failed,
        "criteria_abstained": n_abstained,
        "criteria": crit_out,
        "judge_model": "council",
        "judge_council": {
            "members": [r.get("effective_model", r["model"]) for r in results],
            "surviving": [r.get("effective_model", r["model"]) for r in surviving],
            "failed": [
                {"model": r.get("effective_model", r["model"]), "error": r.get("error", "")}
                for r in results if not r.get("ok")
            ],
            "aggregation": "unanimous_or_sonnet_tiebreak",
            "per_member_user_chars": {
                r["family"]: int(r.get("user_chars", 0) or 0) for r in results
            },
            "per_member_verdict_count": {
                r["family"]: len(r["verdicts"]) for r in surviving
            },
            "headroom_enabled": headroom_enabled,
            "headroom_tokens_saved_total": headroom_tokens_saved_total,
            "headroom_per_member": headroom_per_member,
        },
        "truncation_flags": truncation_flags,
        "abstention_flags": abstention_flags,
        "usage": council_usage,
    }


def grade_with_rubric(
    rubrics: list,
    task_description: str,
    workspace_results: Path,
    transcript_text: str = "",
    judge_model: str | None = None,
    use_council: bool | None = None,
) -> dict:
    """Score `rubrics` with the LLM judge COUNCIL (m1609 2026-06-09).

    Single-judge mode was removed; the council is the only grading path.
    The `judge_model` and `use_council` parameters are retained for backward
    call-site compatibility but are ignored — every invocation runs the full
    council. Aggregation is unanimous-or-abstain (see `_grade_council`).

    Returns a scores dict:
    {overall_score, rubric_weights_percentage,
     criteria_total, criteria_passed, criteria_failed, criteria_abstained,
     criteria:[...], judge_model:'council', judge_council:{...},
     truncation_flags, abstention_flags, usage}
    or {overall_score:0.0, error:...} when no rubrics or no council members
    are configured (never raises)."""
    if not rubrics:
        return {"overall_score": 0.0, "error": "no rubric criteria"}
    system = _judge_system_prompt()

    members = council_members()
    if not members:
        return {
            "overall_score": 0.0,
            "error": "no judge council members configured (set JUDGE_COUNCIL_SONNET_ARN / _GLM_ARN / _KIMI_ARN, or JUDGE_COUNCIL_MEMBERS) in .env",
            "usage": dict(_ZERO_USAGE),
        }

    validate_judge_pricing(members)

    user_for_member: dict[str, str] = {}
    for m in members:
        budget = _member_evidence_budget(m.model, m.family)
        ev = _gather_evidence(workspace_results, transcript_text, budget=budget)
        user_for_member[m.model] = _judge_user_prompt(task_description, rubrics, ev)
    return _grade_council(rubrics, system, user_for_member, members)

def _write_score(output_dir: Path, task_id: str, scores: dict) -> None:
    score_path = output_dir / "score.json"
    score_path.parent.mkdir(parents=True, exist_ok=True)
    score_path.write_text(
        json.dumps(scores, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    logger.info("[%s] Grading results written to → %s", task_id, score_path)


def _error_score(output_dir: Path, task_id: str, message: str) -> dict:
    scores = {"overall_score": 0.0, "error": message}
    _write_score(output_dir, task_id, scores)
    return scores


def _grading_error(
    output_dir: Path,
    task_id: str,
    message: str,
    write_error_score: bool,
) -> dict:
    if write_error_score:
        return _error_score(output_dir, task_id, message)
    return {"error": message}


def write_error_score(output_dir: Path, task_id: str, message: str) -> dict:
    return _error_score(output_dir, task_id, message)


def run_grading(
    task_id: str,
    automated_checks: str,
    output_dir: Path,
    extra_env: str = "",
    lobster_env: list[str] | None = None,
    transcript_container_path: str = "",
    write_error_score: bool = False,
) -> dict:
    logger.info("[%s] Starting in-container grading...", task_id)

    loader_src = Path(__file__).with_name("transcript_loader.py")
    if not loader_src.exists():
        logger.error("[%s] transcript loader module not found: %s", task_id, loader_src)
        return _grading_error(
            output_dir,
            task_id,
            f"transcript loader module not found: {loader_src}",
            write_error_score,
        )

    runner_code = "\n".join([
        "import json",
        "from _transcript_loader import load_transcript",
        f"_transcript = load_transcript({json.dumps(transcript_container_path)})",
        "",
        automated_checks,
        "",
        f'result = grade(transcript=_transcript, workspace_path="{TMP_WORKSPACE}")',
        "print(json.dumps(result))",
    ]) + "\n"

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as f:
        f.write(runner_code)
        runner_host = f.name

    try:
        r_loader = subprocess.run(
            ["docker", "cp", str(loader_src), f"{task_id}:/tmp/_transcript_loader.py"],
            capture_output=True, text=True,
        )
        if r_loader.returncode != 0:
            logger.error("[%s] docker cp transcript loader failed: %s", task_id, r_loader.stderr)
            return _grading_error(
                output_dir,
                task_id,
                f"docker cp transcript loader failed: {r_loader.stderr}",
                write_error_score,
            )

        r = subprocess.run(
            ["docker", "cp", runner_host, f"{task_id}:/tmp/_grade_runner.py"],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            logger.error("[%s] docker cp failed: %s", task_id, r.stderr)
            return _grading_error(
                output_dir,
                task_id,
                f"docker cp failed: {r.stderr}",
                write_error_score,
            )

        env_args: list[str] = []
        for line in extra_env.splitlines():
            key = line.strip()
            if not key or key.startswith("#"):
                continue
            value = os.environ.get(key, "")
            env_args += ["-e", f"{key}={value}"]
            masked = (value[:4] + "***") if value else "(empty)"
            logger.info("[%s] Injecting grading env: %s=%s", task_id, key, masked)

        for key in (lobster_env or []):
            value = os.environ.get(key, "")
            if not value:
                logger.warning("[%s] Grading lobster env key %s not found, skipping", task_id, key)
                continue
            env_args += ["-e", f"{key}={value}"]
            masked = value[:4] + "***"
            logger.info("[%s] Injecting grading lobster env: %s=%s", task_id, key, masked)

        r = subprocess.run(
            ["docker", "exec", *env_args, task_id, "python3", "/tmp/_grade_runner.py"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if r.returncode != 0:
            logger.error("[%s] Grading script execution failed: %s", task_id, r.stderr)
            return _grading_error(
                output_dir,
                task_id,
                f"grade script failed: {r.stderr}",
                write_error_score,
            )

        try:
            scores = json.loads(r.stdout.strip())
        except json.JSONDecodeError:
            scores = None
            for line in reversed(r.stdout.strip().splitlines()):
                line = line.strip()
                if line.startswith("{"):
                    try:
                        scores = json.loads(line)
                        break
                    except json.JSONDecodeError:
                        continue
            if scores is None:
                logger.error("[%s] Failed to parse grading result, no valid JSON found in stdout\nstdout: %s", task_id, r.stdout[:500])
                return _grading_error(
                    output_dir,
                    task_id,
                    "json parse failed: no valid JSON in stdout",
                    write_error_score,
                )

    finally:
        Path(runner_host).unlink(missing_ok=True)

    _write_score(output_dir, task_id, scores)
    return scores


def format_scores(task_id: str, scores: dict) -> str:
    if "error" in scores and not any(
        isinstance(v, (int, float)) for v in scores.values()
    ):
        return f"[{task_id}] Grading error: {scores['error']}"
    lines = [f"\n{'='*60}", f"  {task_id}", f"{'='*60}"]

    for k, v in scores.items():
        if isinstance(v, (int, float)):
            bar = "█" * int(v * 10) + "░" * (10 - int(v * 10))
            lines.append(f"  {bar} {v:.2f}  {k}")

    lines.append("=" * 60)
    return "\n".join(lines)

def print_summary(results: list[dict], category: str, output_dir: Path, model_name: str,
                  quiet: bool = False) -> None:
    # quiet=True suppresses the ASCII console report (the Rich execution summary
    # in eval/run_batch.py renders it instead) while preserving the JSON write
    # below. Shadowing `print` for the whole function keeps every line unchanged.
    import builtins as _b
    print = _b.print if not quiet else (lambda *a, **k: None)  # noqa: A001
    print(f"\n{'#'*60}")
    print(f"  Summary Report — {category}")
    print(f"{'#'*60}")

    all_scores: dict[str, float] = {}
    for r in results:
        task_id = r["task_id"]
        scores = r['scores']
        if not scores:
            if r.get("error"):
                print(f"  ✗ {task_id}: {r['error']}")
            else:
                print(f"  - {task_id}: No scores")
            continue
        numeric_dict = {k: v for k, v in scores.items() if isinstance(v, (int, float))}
        
        if not numeric_dict:
            if "error" in scores:
                print(f"  ✗ {task_id}: Grading error {scores['error']}")
            else:
                print(f"  - {task_id}: No valid numeric scores")
            continue

        avg = sum(numeric_dict.values()) / len(numeric_dict)
        status = "!" if r.get("error") or scores.get("error") else "✓"
        note = ""
        if r.get("error"):
            note = f" agent_error={r['error']}"
        elif scores.get("error"):
            note = f" grading_error={scores['error']}"
        print(f"  {status} {task_id}: avg {avg:.2f}  ({len(numeric_dict)} items){note}")

        final_score_val = numeric_dict.get('overall_score', avg)
        all_scores[task_id] = final_score_val

    if all_scores:
        print(f"\n  Final scores per task:")
        for k, score in sorted(all_scores.items()):
            bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
            print(f"    {bar} {score:.2f}  {k}")

    print(f"\n  Token usage and cost per task:")
    print(f"    {'Task ID':<55} {'Output Tokens':>12} {'Cost(USD)':>12}")
    print(f"    {'-'*55} {'-'*12} {'-'*12}")
    total_output_tokens = 0
    total_cost_usd = 0.0
    for r in sorted(results, key=lambda x: x["task_id"]):
        usage = r.get("usage", {})
        out_tok = usage.get("output_tokens", 0)
        cost = usage.get("cost_usd", 0.0)
        total_output_tokens += out_tok
        total_cost_usd += cost
        print(f"    {r['task_id']:<55} {out_tok:>12} {cost:>11.4f}$")
    print(f"    {'Total':<55} {total_output_tokens:>12} {total_cost_usd:>11.4f}$")

    summary_path = output_dir / category / f"summary_{model_name}.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        json.dumps(results, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"\n  Summary written to → {summary_path}")
    print("#" * 60)

    if quiet:
        # The verbose ASCII report above is suppressed under quiet mode (the Rich
        # execution summary renders it instead). Keep a compact, greppable marker
        # in the log so downstream tooling that keys on the old "Summary Report —
        # <category>" header still finds the report. Routed through the logger,
        # never raw print, so it reaches logs/*.log on the default path without
        # corrupting the Textual dashboard's full-screen canvas.
        logger.info("Summary Report — %s | %d task(s) | written to %s",
                    category, len(results), summary_path)

_MODEL_COST_PER_TOKEN: dict[str, tuple[float, float]] = {
    "gpt-5.5":            (0.000005,  0.00003),
    "gpt-4o":             (0.0000025, 0.00001),
    "claude-opus-4.7":    (0.000005,  0.000025),
    "claude-sonnet-4.6":  (0.000003,  0.000015),
}


def _extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for c in content:
            if isinstance(c, str):
                parts.append(c)
            elif isinstance(c, dict):
                parts.append(str(c.get("text") or c.get("content") or ""))
        return "\n".join(parts)
    return ""


def _estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, (len(text) + 3) // 4)


def extract_usage_from_litellm_log(
    log_path: Path, window_start: float, window_end: float
) -> dict:
    totals = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "total_tokens": 0,
        "audio_seconds": 0.0,
        "cost_usd": 0.0,
        "request_count": 0,
        "usage_source": "litellm",
    }
    if not log_path or not log_path.exists():
        return totals

    from datetime import datetime as _dt

    pad = 2.0
    lo = window_start - pad
    hi = window_end + pad

    try:
        lines = log_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return totals

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts_str = row.get("ts", "")
        try:
            ts = _dt.fromisoformat(ts_str.replace("Z", "+00:00")).timestamp()
        except (ValueError, AttributeError):
            continue
        if ts < lo or ts > hi:
            continue
        if row.get("kind") == "preflight":
            continue
        totals["request_count"] += 1
        totals["input_tokens"]       += int(row.get("input_tokens", 0) or 0)
        totals["output_tokens"]      += int(row.get("output_tokens", 0) or 0)
        totals["cache_read_tokens"]  += int(row.get("cache_read_tokens", 0) or 0)
        totals["cache_write_tokens"] += int(row.get("cache_write_tokens", 0) or 0)
        totals["total_tokens"]       += int(row.get("total_tokens", 0) or 0)
        totals["audio_seconds"]      += float(row.get("audio_seconds", 0.0) or 0.0)
        totals["cost_usd"]           += float(row.get("cost_usd", 0.0) or 0.0)

    totals["cost_usd"] = round(totals["cost_usd"], 6)
    totals["audio_seconds"] = round(totals["audio_seconds"], 3)
    return totals


def extract_preflight_usage_from_litellm_log(log_path: Path) -> dict:
    # Aggregates every row tagged kind="preflight" in the LiteLLM callback log,
    # with no time-window filter. Preflight runs once per sidecar startup
    # (eval/run_batch.py::verify_litellm_upstream_reachable), BEFORE any task's
    # run window, so the in-window agent extractor skips it. Per user policy
    # (m1402, "All tasks" attribution), every task in the batch picks up the
    # same preflight cost so each task's usage.json reflects the true LLM
    # traffic that occurred during its execution. Returns the agent-shaped
    # totals dict (zero values when no preflight ran) so save_usage can drop
    # it straight into sources["preflight"].
    totals = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "total_tokens": 0,
        "audio_seconds": 0.0,
        "cost_usd": 0.0,
        "request_count": 0,
        "usage_source": "litellm",
    }
    if not log_path or not log_path.exists():
        return totals
    try:
        lines = log_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return totals
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("kind") != "preflight":
            continue
        totals["request_count"] += 1
        totals["input_tokens"]       += int(row.get("input_tokens", 0) or 0)
        totals["output_tokens"]      += int(row.get("output_tokens", 0) or 0)
        totals["cache_read_tokens"]  += int(row.get("cache_read_tokens", 0) or 0)
        totals["cache_write_tokens"] += int(row.get("cache_write_tokens", 0) or 0)
        totals["total_tokens"]       += int(row.get("total_tokens", 0) or 0)
        totals["audio_seconds"]      += float(row.get("audio_seconds", 0.0) or 0.0)
        totals["cost_usd"]           += float(row.get("cost_usd", 0.0) or 0.0)
    totals["cost_usd"] = round(totals["cost_usd"], 6)
    totals["audio_seconds"] = round(totals["audio_seconds"], 3)
    return totals


def extract_oauth_usage_from_litellm_log(
    log_path: Path,
    window_start_ts: str = "",
    window_end_ts: str = "",
) -> dict:
    totals = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "total_tokens": 0,
        "cost_actual": 0.0,
        "cost_bedrock_equivalent": 0.0,
        "request_count": 0,
        "usage_source": "litellm_oauth",
        "route": "claude_oauth_bridge",
    }
    try:
        if not log_path or not Path(log_path).exists():
            return totals
        lines = Path(log_path).read_text(encoding="utf-8").splitlines()
    except OSError:
        return totals
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if window_start_ts and row.get("ts", "") < window_start_ts:
            continue
        if window_end_ts and row.get("ts", "") > window_end_ts:
            continue
        totals["request_count"] += 1
        totals["input_tokens"]       += int(row.get("input_tokens", 0) or 0)
        totals["output_tokens"]      += int(row.get("output_tokens", 0) or 0)
        totals["cache_read_tokens"]  += int(row.get("cache_read_tokens", 0) or 0)
        totals["cache_write_tokens"] += int(row.get("cache_write_tokens", 0) or 0)
        totals["cost_actual"]        += float(row.get("cost_actual", 0.0) or 0.0)
        totals["cost_bedrock_equivalent"] += float(row.get("cost_bedrock_equivalent", 0.0) or 0.0)
    totals["total_tokens"] = (
        totals["input_tokens"] + totals["output_tokens"]
        + totals["cache_read_tokens"] + totals["cache_write_tokens"]
    )
    totals["cost_actual"] = round(totals["cost_actual"], 6)
    totals["cost_bedrock_equivalent"] = round(totals["cost_bedrock_equivalent"], 6)
    return totals


def extract_usage_from_jsonl(jsonl_path: Path) -> dict:
    totals = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "total_tokens": 0,
        "audio_seconds": 0.0,
        "cost_usd": 0.0,
        "request_count": 0,
        "usage_source": "openclaw",
    }
    if not jsonl_path.exists():
        return totals

    entries: list[dict] = []
    for line in jsonl_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    openclaw_total = 0
    last_model = ""
    for entry in entries:
        if entry.get("type") != "message":
            continue
        msg = entry.get("message", {})
        if msg.get("role") != "assistant":
            continue
        totals["request_count"] += 1
        if msg.get("model"):
            last_model = msg["model"]
        usage = msg.get("usage", {})
        totals["input_tokens"]       += usage.get("input",       0)
        totals["output_tokens"]      += usage.get("output",      0)
        totals["cache_read_tokens"]  += usage.get("cacheRead",   0)
        totals["cache_write_tokens"] += usage.get("cacheWrite",  0)
        totals["total_tokens"]       += usage.get("totalTokens", 0)
        cost = usage.get("cost", {})
        totals["cost_usd"] += cost.get("total", 0.0)
        openclaw_total += usage.get("input", 0) + usage.get("output", 0)

    # Fallback: openclaw reported no usage but there were requests. Estimate
    # tokens (~len/4) with a running-context model and apply per-model rates.
    if openclaw_total == 0 and totals["request_count"] > 0:
        totals["usage_source"] = "estimated"
        running_context_tokens = 0
        for entry in entries:
            if entry.get("type") != "message":
                continue
            msg = entry.get("message", {})
            text = _extract_text(msg.get("content", ""))
            tokens = _estimate_tokens(text)
            role = msg.get("role")
            if role in ("user", "system", "toolResult"):
                running_context_tokens += tokens
            elif role == "assistant":
                totals["input_tokens"]  += running_context_tokens
                totals["output_tokens"] += tokens
                running_context_tokens += tokens
                if msg.get("model"):
                    last_model = msg["model"]
        totals["total_tokens"] = totals["input_tokens"] + totals["output_tokens"]

        model_id = last_model.split("/")[-1] if last_model else ""
        rates = _MODEL_COST_PER_TOKEN.get(model_id, (0.0, 0.0))
        totals["cost_usd"] = (
            totals["input_tokens"]  * rates[0]
            + totals["output_tokens"] * rates[1]
        )

    # Mark missing-price $0 (e.g. OpenRouter-only models) so it is not read as "free".
    if totals["cost_usd"] == 0.0 and totals["request_count"] > 0:
        model_id = last_model.split("/")[-1] if last_model else ""
        if model_id not in _MODEL_COST_PER_TOKEN:
            totals["cost_unpriced"] = True

    totals["cost_usd"] = round(totals["cost_usd"], 6)
    return totals

def print_global_summary(results: list[dict], output_dir: Path, model_name: str,
                         quiet: bool = False) -> None:
    # quiet=True suppresses the ASCII console report (Rich renders it) while
    # preserving any JSON side effects below. See print_summary for rationale.
    import builtins as _b
    print = _b.print if not quiet else (lambda *a, **k: None)  # noqa: A001
    print(f"\n{'#'*60}")
    print(f"  Global Summary Report — ALL CATEGORIES")
    print(f"{'#'*60}")

    total_tasks = len(results)
    scored_tasks = 0
    missing_score_tasks = 0
    total_score = 0.0
    for r in results:
        scores = r.get("scores", {})
        numeric = {
            k: v
            for k, v in scores.items()
            if isinstance(v, (int, float))
        } if scores else {}
        if not numeric:
            missing_score_tasks += 1
            continue
        final = numeric.get("overall_score", sum(numeric.values()) / len(numeric))
        total_score += final
        scored_tasks += 1

    global_avg = 0.0
    if total_tasks > 0:
        global_avg = total_score / total_tasks
        bar = "█" * int(global_avg * 10) + "░" * (10 - int(global_avg * 10))
        print(f"\n  Completed tasks: {scored_tasks} / {total_tasks}")
        print(f"  Tasks without a valid score.json: {missing_score_tasks}")
        if missing_score_tasks > 0:
            print("  Possible causes: task execution failed, such as OOM, or grading failed.")
        print(f"  Global average: {bar} {global_avg:.4f}")
    else:
        print("  No tasks found")

    total_out_tok = sum(r.get("usage", {}).get("output_tokens", 0) for r in results)
    total_cost    = sum(r.get("usage", {}).get("cost_usd",      0.0) for r in results)
    print(f"  Total output tokens: {total_out_tok}   Total cost: ${total_cost:.4f}")

    summary_path = output_dir / f"summary_all_{model_name}.json"
    summary_path.write_text(
        json.dumps(
            {"global_avg": global_avg if total_tasks else None,
             "task_count": total_tasks,
             "scored_task_count": scored_tasks,
             "missing_score_task_count": missing_score_tasks,
             "results": results},
            indent=2, ensure_ascii=False, default=str,
        ),
        encoding="utf-8",
    )
    print(f"\n  Global summary written to → {summary_path}")
    print("#" * 60)

    if quiet:
        # See print_summary: keep a compact, greppable marker in the log for
        # scrapers keying on the old "Global Summary Report — ALL CATEGORIES"
        # header when the ASCII report is suppressed. Logger, not raw print.
        logger.info("Global Summary Report — ALL CATEGORIES | %d task(s) | written to %s",
                    total_tasks, summary_path)
