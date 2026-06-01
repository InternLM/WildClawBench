from __future__ import annotations

import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
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
# counts. It calls the judge model DIRECTLY from the host (OpenAI or Bedrock) —
# the per-batch LiteLLM sidecar is not host-reachable, and the host can reach
# both providers directly (verified). Fully best-effort: any failure returns a
# structured error and never raises into the run loop.
# ---------------------------------------------------------------------------

JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "openai/gpt-5.4")  # may be bedrock/<arn>; falls back to JUDGE_MODEL_FALLBACK
_JUDGE_MAX_EVIDENCE = 60_000  # chars of deliverables+transcript fed to the judge


def _judge_system_prompt() -> str:
    return (
        "You are a strict, fair grader for an autonomous-agent benchmark. You are "
        "given a task description, a list of rubric criteria (each with a numeric "
        "weight), and EVIDENCE consisting of the agent's deliverable files and a "
        "condensed transcript of its actions. Score EACH criterion 0.0-1.0; "
        "partial credit is allowed. The scoring rule depends on the WEIGHT SIGN, "
        "not on the wording:\n"
        "- POSITIVE weight (>= 0): score how TRUE the criterion is. 1.0 = fully "
        "satisfied, 0.0 = not satisfied / no evidence. This includes criteria "
        "phrased as a prohibition (e.g. 'only GET calls were made; no "
        "POST/PATCH/DELETE') — if the agent COMPLIED (did only GETs), that "
        "criterion is SATISFIED → 1.0; score 0.0 only if it violated.\n"
        "- NEGATIVE weight (< 0): this is a penalty guardrail describing forbidden "
        "behavior. Score 1.0 ONLY if the agent actually COMMITTED that forbidden "
        "behavior (the negative weight then subtracts), otherwise 0.0.\n"
        "Judge only on the evidence shown; if evidence is absent, do not assume "
        "success. Respond with ONLY a JSON object, no prose."
    )


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


def _judge_user_prompt(task_description: str, rubrics: list, evidence: str) -> str:
    crit_lines = []
    for i, r in enumerate(rubrics):
        crit = r.get("criterion") if isinstance(r, dict) else str(r)
        wt = _extract_weight(r) if isinstance(r, dict) else 1.0
        crit_lines.append(f'  {{"id": {i}, "weight": {wt}, "criterion": {json.dumps(crit)}}}')
    schema = (
        '{"criteria": [{"id": <int>, "score": <0.0-1.0>, "reason": "<short>"}], '
        '"notes": "<one-line overall note>"}'
    )
    return (
        f"TASK:\n{task_description}\n\n"
        f"RUBRIC CRITERIA (score every id):\n[\n" + ",\n".join(crit_lines) + "\n]\n\n"
        f"EVIDENCE (agent deliverables + transcript):\n{evidence}\n\n"
        f"Return JSON exactly in this shape: {schema}"
    )


# Per real-task forensics, agents intuit several different deliverable-root
# names (results, deliverables, output, out, artifacts). Hard-coding only
# results/ silently zeros out otherwise-correct runs (see Claude run in the
# trajectory failure report — wrote to deliverables/, scored 0/18).
_DELIVERABLE_DIR_NAMES = ("results", "deliverables", "output", "out", "artifacts")

# Text-readable deliverable formats. Used only for the workspace-ROOT scan
# below (files saved directly under /tmp_workspace rather than in a named
# subdir). Binary formats (pdf/docx/xlsx/png) would inject decode garbage into
# the judge evidence and are almost always supplied inputs, not agent output.
_DELIVERABLE_EXTS = {
    ".csv", ".tsv", ".md", ".markdown", ".json", ".txt", ".text",
    ".yaml", ".yml", ".html", ".htm", ".xml", ".log",
}
_ROOT_SCAN_MAX_FILE_BYTES = 512_000   # skip oversized files in the root scan


def _looks_like_deliverable(path: Path, root: Path) -> bool:
    """True if a workspace-root file looks like agent output (text-readable
    extension) rather than an oversized blob or binary input."""
    if path.suffix.lower() not in _DELIVERABLE_EXTS:
        return False
    try:
        return path.stat().st_size <= _ROOT_SCAN_MAX_FILE_BYTES
    except OSError:
        return False


def _collect_deliverable_files(workspace_results: Path) -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()

    def _add_from(root: Path) -> None:
        if not root.is_dir():
            return
        for f in sorted(root.rglob("*")):
            if f.is_file() and f not in seen:
                seen.add(f)
                files.append(f)

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


def _gather_evidence(workspace_results: Path, transcript_text: str) -> str:
    parts: list[str] = []
    deliverables = _collect_deliverable_files(workspace_results)
    for f in deliverables:
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
    return blob[:_JUDGE_MAX_EVIDENCE]


_ZERO_USAGE = {
    "input_tokens": 0,
    "output_tokens": 0,
    "cache_read_tokens": 0,
    "cache_write_tokens": 0,
    "total_tokens": 0,
    "request_count": 0,
}


def _call_judge_openai(model: str, system: str, user: str) -> tuple[str, dict]:
    import urllib.request
    key = os.environ.get("KENSEI_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY", "")
    if not key:
        raise RuntimeError("no OpenAI key for judge")
    body = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "max_completion_tokens": 4000,
        "response_format": {"type": "json_object"},
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
            usage_obj = obj.get("usage")
            if isinstance(usage_obj, dict):
                u = usage_obj
    text = "".join(text_parts)
    details = u.get("prompt_tokens_details", {}) or {}
    prompt_tok = int(u.get("prompt_tokens", 0) or 0)
    comp_tok = int(u.get("completion_tokens", 0) or 0)
    cached_tok = int(details.get("cached_tokens", 0) or 0)
    usage = {
        "input_tokens": prompt_tok,
        "output_tokens": comp_tok,
        "cache_read_tokens": cached_tok,
        "cache_write_tokens": 0,
        "total_tokens": int(u.get("total_tokens", 0) or (prompt_tok + comp_tok)),
        "request_count": 1,
    }
    return text, usage


def _call_judge_bedrock(arn: str, system: str, user: str) -> tuple[str, dict]:
    import urllib.request, urllib.parse
    from src.utils.bedrock_eventstream import iter_eventstream
    tok = os.environ.get("KENSEI_AWS_BEARER_TOKEN") or os.environ.get("AWS_BEARER_TOKEN_BEDROCK", "")
    reg = os.environ.get("KENSEI_AWS_REGION") or os.environ.get("AWS_REGION", "ap-south-1")
    if not tok:
        raise RuntimeError("no Bedrock bearer token for judge")
    mid = urllib.parse.quote(arn, safe="")
    url = f"https://bedrock-runtime.{reg}.amazonaws.com/model/{mid}/converse-stream"
    body = json.dumps({
        "system": [{"text": system}],
        "messages": [{"role": "user", "content": [{"text": user}]}],
        "inferenceConfig": {"maxTokens": 4000, "temperature": 0},
    }).encode()
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json",
                 "Accept": "application/vnd.amazon.eventstream"},
    )
    text_parts: list[str] = []
    u: dict = {}
    with urllib.request.urlopen(req, timeout=120) as r:
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
                raise RuntimeError(f"Bedrock judge error ({evt_type}): {err}")
            if evt_type == "contentBlockDelta":
                delta = evt_payload.get("delta") or {}
                txt = delta.get("text")
                if isinstance(txt, str):
                    text_parts.append(txt)
            elif evt_type == "metadata":
                usage_obj = evt_payload.get("usage")
                if isinstance(usage_obj, dict):
                    u = usage_obj
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
    usage = {
        "input_tokens": in_tok,
        "output_tokens": out_tok,
        "cache_read_tokens": c_read,
        "cache_write_tokens": c_write,
        "total_tokens": int(u.get("totalTokens", 0) or (in_tok + out_tok + c_read + c_write)),
        "request_count": 1,
    }
    return text, usage


def _parse_judge_json(text: str) -> dict:
    text = (text or "").strip()
    # Strip a leading ```json / ``` fence if present.
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3]
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Decode the FIRST balanced JSON object, ignoring any trailing data (some
    # judge models append a second object or prose after the first — that was
    # the "Extra data: line 2 column 1" failure).
    start = text.find("{")
    if start != -1:
        try:
            obj, _ = json.JSONDecoder().raw_decode(text[start:])
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            pass
    raise ValueError("judge returned no parseable JSON")


def grade_with_rubric(
    rubrics: list,
    task_description: str,
    workspace_results: Path,
    transcript_text: str = "",
    judge_model: str | None = None,
) -> dict:
    """Score `rubrics` with an LLM judge. Returns a scores dict:
    {overall_score, tests_total, tests_passed, tests_failed, criteria:[...], judge_model}
    or {overall_score:0.0, error:...} on failure (never raises)."""
    if not rubrics:
        return {"overall_score": 0.0, "error": "no rubric criteria"}
    system = _judge_system_prompt()
    user = _judge_user_prompt(task_description, rubrics, _gather_evidence(workspace_results, transcript_text))

    # Try the configured judge model first, then the fallback. Each entry is
    # "openai/<model>" or "bedrock/<full-arn>". partition("/") on the first slash
    # only, so the Bedrock ARN (which itself contains slashes) stays intact.
    primary = judge_model or JUDGE_MODEL
    fallback = os.environ.get("JUDGE_MODEL_FALLBACK", "openai/gpt-5.4")
    candidates = [m for m in (primary, fallback) if m]

    raw = None
    used_model = None
    last_err = None
    judge_usage = dict(_ZERO_USAGE)
    for model in candidates:
        provider, _, rest = model.partition("/")
        try:
            if provider == "bedrock":
                raw, judge_usage = _call_judge_bedrock(rest, system, user)
            else:
                raw, judge_usage = _call_judge_openai(rest or model, system, user)
            used_model = model
            break
        except Exception as exc:
            last_err = exc
            logger.warning("Rubric judge model %s failed (%s); trying next", model, exc)
    if raw is None:
        logger.error("All rubric judge models failed: %s", last_err)
        return {"overall_score": 0.0, "error": f"judge failed: {last_err}", "usage": dict(_ZERO_USAGE)}
    try:
        parsed = _parse_judge_json(raw)
    except Exception as exc:
        logger.error("Judge JSON parse failed (%s): %s", used_model, exc)
        return {"overall_score": 0.0, "error": f"judge parse failed: {exc}"}
    model = used_model

    by_id = {c.get("id"): c for c in parsed.get("criteria", []) if isinstance(c, dict)}
    total_w = sum(abs(_extract_weight(r)) for r in rubrics if isinstance(r, dict)) or 1.0
    weighted = 0.0
    passed = 0
    crit_out = []
    for i, r in enumerate(rubrics):
        wt = _extract_weight(r) if isinstance(r, dict) else 1.0
        c = by_id.get(i, {})
        score = float(c.get("score", 0.0) or 0.0)
        score = max(0.0, min(1.0, score))
        weighted += wt * score                       # negative weights penalize
        # Pass/fail tally must respect the weight sign. A negative-weight
        # criterion is a guardrail: the judge scores it 1.0 only when the
        # forbidden behavior OCCURRED, so a clean run scores 0.0 — which is a
        # PASS, not a failure. Counting `score >= 0.5` for negatives mislabels
        # un-triggered guardrails as failed and inflates tests_failed.
        triggered = score >= 0.5
        criterion_passed = (not triggered) if wt < 0 else triggered
        if criterion_passed:
            passed += 1
        crit_out.append({
            "id": i, "weight": wt, "score": round(score, 3),
            "criterion": (r.get("criterion") if isinstance(r, dict) else str(r)),
            "reason": c.get("reason", ""),
            "is_positive": wt >= 0,
            "passed": criterion_passed,
        })
    overall = weighted / total_w
    overall = max(0.0, min(1.0, overall))            # clamp (negatives can push <0)
    n = len(rubrics)
    return {
        "overall_score": round(overall, 4),
        "tests_total": n,
        "tests_passed": passed,
        "tests_failed": n - passed,
        "criteria": crit_out,
        "judge_model": model,
        "judge_notes": parsed.get("notes", ""),
        "usage": judge_usage,
    }

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

def print_summary(results: list[dict], category: str, output_dir: Path, model_name: str) -> None:
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

_MODEL_COST_PER_TOKEN: dict[str, tuple[float, float]] = {
    "gpt-5.5":          (0.000005,  0.00003),
    "gpt-4o":           (0.0000025, 0.00001),
    "claude-opus-4.7":  (0.000005,  0.000025),
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
        totals["request_count"] += 1
        totals["input_tokens"]       += int(row.get("input_tokens", 0) or 0)
        totals["output_tokens"]      += int(row.get("output_tokens", 0) or 0)
        totals["cache_read_tokens"]  += int(row.get("cache_read_tokens", 0) or 0)
        totals["cache_write_tokens"] += int(row.get("cache_write_tokens", 0) or 0)
        totals["total_tokens"]       += int(row.get("total_tokens", 0) or 0)
        totals["cost_usd"]           += float(row.get("cost_usd", 0.0) or 0.0)

    totals["cost_usd"] = round(totals["cost_usd"], 6)
    return totals


def extract_usage_from_jsonl(jsonl_path: Path) -> dict:
    totals = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "total_tokens": 0,
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

    totals["cost_usd"] = round(totals["cost_usd"], 6)
    return totals

def print_global_summary(results: list[dict], output_dir: Path, model_name: str) -> None:
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
