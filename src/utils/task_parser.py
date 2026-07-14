from __future__ import annotations

import json
import logging
import mimetypes
import os
import re
from pathlib import Path
from typing import Any, Optional
from dotenv import load_dotenv

import yaml

load_dotenv()
logger = logging.getLogger(__name__)
# Resolve task-relative paths from repository root, not src/.
ROOT_DIR = Path(__file__).resolve().parents[2]


def parse_task_md(task_file: Path) -> dict:
    """Extract task_id, prompt, workspace_path, and automated_checks from task.md."""
    content = task_file.read_text(encoding="utf-8")

    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
    if not fm_match:
        raise ValueError(f"YAML frontmatter not found: {task_file}")

    metadata = yaml.safe_load(fm_match.group(1))
    body     = fm_match.group(2)

    sections: dict[str, str] = {}
    current_section: Optional[str] = None
    lines: list[str] = []
    for line in body.split("\n"):
        header = re.match(r"^##\s+(.+)$", line)
        if header:
            if current_section is not None:
                sections[current_section] = "\n".join(lines).strip()
            current_section = header.group(1)
            lines = []
        else:
            lines.append(line)
    if current_section is not None:
        sections[current_section] = "\n".join(lines).strip()

    def strip_codeblock(raw: str) -> str:
        s = re.sub(r"^```[^\n]*\n?", "", raw.strip())
        s = re.sub(r"\n?```$", "", s).strip()
        return s

    prompt = sections.get("Prompt", "").strip()

    raw_workspace  = sections.get("Workspace Path", "").strip()
    workspace_path = strip_codeblock(raw_workspace)
    if not workspace_path:
        raise ValueError(f"Missing ## Workspace Path in task.md: {task_file}")

    skills_path = "skills"

    automated_checks = strip_codeblock(sections.get("Automated Checks", ""))
    env    = strip_codeblock(sections.get("Env",    ""))
    skills = strip_codeblock(sections.get("Skills",    ""))
    warmup = strip_codeblock(sections.get("Warmup", ""))

    task_id         = metadata.get("id",             task_file.stem)
    timeout_seconds = int(metadata.get("timeout_seconds", 120))

    wp = Path(workspace_path)
    if not wp.is_absolute():
        wp = (ROOT_DIR / wp).resolve()
    workspace_path = str(wp)

    sp = Path(skills_path)
    if not sp.is_absolute():
        sp = (ROOT_DIR / sp).resolve()
    skills_path = str(sp)

    return {
        "task_id":          task_id,
        "prompt":           prompt,
        "workspace_path":   workspace_path,
        "skills_path":      skills_path,
        "automated_checks": automated_checks,
        "env":              env,
        "skills":           skills,
        "warmup":           warmup,
        "timeout_seconds":  timeout_seconds,
        "file_path":        str(task_file.resolve()),
        "category":         task_file.parent.name,
    }


# ---------------------------------------------------------------------------
# Multi-format dispatcher (kensei-parity): markdown | yaml | native directory.
# run_batch.py uses load_task() for directories and falls back to parse_task_md
# for .md files so existing behavior is preserved exactly.
# ---------------------------------------------------------------------------

def load_task(path: str | Path) -> dict:
    """Load a task from a .md file or a native task directory.

    Task content authority:
    - Native dir = prompt.txt + rubric.json (+ persona/ (SOUL/MEMORY/AGENTS) + data/
      (input artifacts) + mock_data/ + tests). This is the sole source of truth for
      prompt body, rubric, tests, and attachments.
    - task.yaml (optional sidecar) carries METADATA + connector declarations ONLY:
      difficulty, modalities, l1/l2, task_type, required_apis, distractor_apis (per b3).
      It is overlaid on top of the native dict via `_overlay_yaml_metadata`; it CANNOT
      supply prompt text, rubrics, tests, attachments, or persona — those keys are
      ignored if present in YAML.
    - .md tasks use parse_task_md (unchanged fork behavior), normalized superset.

    The directory dispatcher therefore always prefers prompt.txt+rubric.json native
    loading when present, then overlays task.yaml on top. A bare YAML file path (no
    sibling prompt.txt) is rejected so callers cannot accidentally use YAML as a
    standalone task format (regression observed with layla_mcbride trajectory
    2026-06-05T22:04:30 where YAML-only loading produced an empty user prompt and
    the model asked "What do you need me to solve?").
    """
    p = Path(path)
    if p.is_dir():
        md = p / "task.md"
        if md.is_file():
            return _attach_drift_script(load_task(md), p)
        # Native layout accepts prompt.txt (single prompt), prompts.txt (Talos
        # inject-format per-turn wake-up script; see inject_director.py) or
        # PROMPT.md (TURN-delimited or plain), always alongside rubric.json.
        if ((p / "prompt.txt").is_file() or (p / "prompts.txt").is_file()
                or (p / "PROMPT.md").is_file()) and (p / "rubric.json").is_file():
            base = _load_native_task(p)
            for cand in ("task.yaml", "task.yml"):
                yf = p / cand
                if yf.is_file():
                    base = _overlay_yaml_metadata(base, yf)
                    break
            return _attach_drift_script(base, p)
        raise FileNotFoundError(
            f"No task content in {p}: native layout requires prompt.txt (or "
            "prompts.txt / PROMPT.md) + rubric.json. task.yaml alone is not a "
            "valid task (it is a metadata sidecar)."
        )
    suffix = p.suffix.lower()
    if suffix in (".yaml", ".yml"):
        raise ValueError(
            f"task.yaml is a metadata sidecar, not a standalone task format. "
            f"Pass the task directory ({p.parent}) instead of the YAML file."
        )
    if suffix == ".md":
        base = parse_task_md(p)
        # Augment the md dict with the uniform superset used by the kensei flow.
        base.setdefault("initial_prompt", base.get("prompt", ""))
        base.setdefault("persona", "marcus")
        base.setdefault("persona_dir", "")
        base.setdefault("rubrics", [])
        base.setdefault("task_dir", str(p.parent))
        base.setdefault("gt_dir", str(p.parent / "gt") if (p.parent / "gt").is_dir() else "")
        base.setdefault("attachments", [])
        base.setdefault("format", "md")
        return _attach_drift_script(base, p.parent)
    raise ValueError(f"Unsupported task file format: {p.suffix}")


def _load_provided_tests(task_dir: Path) -> tuple[str, str]:
    """Load a hand-authored test suite shipped with the task, if present.

    When a task directory provides BOTH ``test_outputs.py`` and
    ``test_weights.json`` (at the task root or under ``tests/``), the harness
    executes those verbatim instead of LLM-generating a suite. The generate-vs-
    execute gate in eval/run_batch.py only generates when ``task["test_code"]``
    is empty, so populating it here transparently skips generation and routes
    straight to src/utils/test_executor.py.

    Requiring ``test_weights.json`` as the opt-in signal is deliberate: legacy
    fixture-based ``test_outputs.py`` files (e.g. input/alden-croft/) ship no
    weights and are incompatible with the no-fixture runner, so they stay on the
    LLM-generation path.

    The suite must match the runner contract in test_executor.py: top-level
    ``Test*`` classes with ``test_*(self)`` methods, no pytest fixtures, stdlib
    only, and mock-API URLs read from ``<SERVICE>_URL`` env vars.

    The suite file may be named ``test_outputs.py`` (canonical) or
    ``test_output.py`` (a common singular-typo variant emitted by some
    generators); both are accepted so a single dropped ``s`` does not silently
    route the task to the LLM-generation fallback. ``test_outputs.py`` wins when
    both exist.

    Returns ``(test_code, test_weights_json)`` — ``test_weights_json`` is the raw
    file text (the executor consumes a JSON string). Returns ``("", "")`` when no
    complete provided suite is found.
    """
    for sub in ("", "tests"):
        base = task_dir / sub if sub else task_dir
        weights_f = base / "test_weights.json"
        if not weights_f.is_file():
            continue
        code_f = None
        for fname in ("test_outputs.py", "test_output.py"):
            cand = base / fname
            if cand.is_file():
                code_f = cand
                break
        if code_f is None:
            continue
        try:
            code = code_f.read_text(encoding="utf-8")
            weights = weights_f.read_text(encoding="utf-8")
        except OSError:
            continue
        if code.strip() and weights.strip():
            return code, weights
    return "", ""


def _load_checkers_and_conftest(task_dir: Path) -> tuple[str, str]:
    """Load the deterministic CHECKERS module (task.py) and its conftest.py.

    Fixture-based suites (``def test_x(state, task_checkers)``) import their
    deterministic checkers from a sibling ``task.py`` (``CHECKERS`` list) and
    take a ``state`` fixture from a ``conftest.py``. The harness ships task.py
    into the test sandbox so the ``task_checkers`` fixture resolves, and writes
    both into the published bundle's ``data/tests/`` (task/task.py + conftest).

    Looked up in priority order so both the canonical layout and ALDEN's
    ``Extra files/`` drop work:
      tests/task/task.py, task/task.py, Extra files/task.py, tests/task.py
    Returns ``(checkers_code, conftest_code)`` — empty strings when absent.
    """
    checkers_code = ""
    for rel in ("tests/task/task.py", "task/task.py", "Extra files/task.py", "tests/task.py"):
        cand = task_dir / rel
        if cand.is_file():
            try:
                checkers_code = cand.read_text(encoding="utf-8")
            except OSError:
                checkers_code = ""
            if checkers_code.strip():
                break
    conftest_code = ""
    for rel in ("tests/conftest.py", "conftest.py", "Extra files/conftest.py"):
        cand = task_dir / rel
        if cand.is_file():
            try:
                conftest_code = cand.read_text(encoding="utf-8")
            except OSError:
                conftest_code = ""
            if conftest_code.strip():
                break
    return checkers_code, conftest_code


def _attach_drift_script(task: dict, task_dir: Path) -> dict:
    # Surface drift.yaml / drift.yml on the task dict so run_batch can start
    # a DriftDirector. Sets to None (not absent) when no script is present so
    # downstream code can use a single key check.
    task["drift_script_path"] = None
    for candidate in ("drift.yaml", "drift.yml"):
        f = task_dir / candidate
        if f.is_file():
            task["drift_script_path"] = str(f.resolve())
            break
    # stages.yaml drives the ClawMark-style multi-turn, inject-while-idle model
    # (silent injection between agent turns). Like drift it needs the admin
    # plane on the per-task mock stack, so run_batch keys admin-plane setup on
    # either key being present.
    task["stages_path"] = None
    for candidate in ("stages.yaml", "stages.yml"):
        f = task_dir / candidate
        if f.is_file():
            task["stages_path"] = str(f.resolve())
            break
    # inject/ dir drives the Talos-style staged injection (per-turn wake-up
    # script in prompts.txt + inject/stageN/mutations.json applied at turn
    # boundaries). Like drift/stages it needs the admin plane on the per-task
    # mock stack. See src/utils/inject_director.py.
    task["inject_path"] = None
    inject_dir = task_dir / "inject"
    if inject_dir.is_dir():
        task["inject_path"] = str(inject_dir.resolve())
    # multi_agent.* config opt-in (sub-agent spawning). Resolution order, highest
    # precedence first:
    #   1. task_config.yaml `multi_agent:` block (explicit, full control).
    #   2. task.yaml `multi_agent_complex_turns: [<1-indexed turn>, ...]` — the
    #      config-driven path: fan-out fires (and is scored) on the turns the
    #      author marked complex, with NO "Multi-Agent" token in the prompts.txt
    #      header required.
    #   3. Legacy fallback: scan prompts.txt for "Multi-Agent" turn-header labels
    #      so older tasks keep working.
    # All three emit the same shape: checker_id = "T<turn_index>_MA", aggregate
    # "MA_C1", min_subagents=2.
    task["multi_agent_config"] = {}
    task["multi_agent_enabled"] = False
    explicit_off = False
    cfg_path = task_dir / "task_config.yaml"
    if cfg_path.is_file():
        try:
            raw = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
            if isinstance(raw, dict):
                ma = raw.get("multi_agent")
                if isinstance(ma, dict):
                    task["multi_agent_config"] = ma
                    task["multi_agent_enabled"] = bool(ma.get("enabled"))
                    # An explicit `enabled: false` is authoritative: it opts the
                    # task OUT of the default-on fallback below.
                    explicit_off = ma.get("enabled") is False
        except (yaml.YAMLError, OSError):
            pass
    if not task["multi_agent_enabled"]:
        n_turns = len(task.get("turn_messages") or []) or None
        synth = _multi_agent_config_from_complex_turns(
            task.get("multi_agent_complex_turns"),
            num_turns=n_turns,
            task_id=task.get("task_id") or task.get("name"),
        )
        if synth.get("enabled"):
            task["multi_agent_config"] = synth
            task["multi_agent_enabled"] = True
    if not task["multi_agent_enabled"]:
        synth = _synthesize_multi_agent_config(task_dir)
        if synth.get("enabled"):
            task["multi_agent_config"] = synth
            task["multi_agent_enabled"] = True
    # Default-ON: with no explicit author decision, enable the sub-agent
    # CAPABILITY by default (the sessions_spawn / subagents tools are exposed) so
    # any task can fan out like the multi-agent reference tasks. This adds NO
    # spawn requirement and NO scoring pressure — the synthesized config has an
    # empty expected_per_turn and no aggregate checker, so build_checker_state
    # emits nothing and _wait_for_subagents is a no-op when nothing spawns.
    # Opt a task out with a task_config.yaml `multi_agent: {enabled: false}`
    # block; disable globally with WCB_MULTI_AGENT_DEFAULT=0. Tasks that want
    # multi-agent SCORED still declare multi_agent_complex_turns / the config.
    if not task["multi_agent_enabled"] and not explicit_off and _multi_agent_default_on():
        task["multi_agent_config"] = _default_multi_agent_config()
        task["multi_agent_enabled"] = True
        logger.info(
            "[%s] multi-agent capability enabled by default (no spawn requirement; "
            "set WCB_MULTI_AGENT_DEFAULT=0 to disable)",
            task.get("task_id") or task.get("name") or "?",
        )
    return task


def _multi_agent_default_on() -> bool:
    """Whether sub-agent capability is enabled by default for tasks that declare
    no multi_agent config. Default ON; set WCB_MULTI_AGENT_DEFAULT to a falsy
    token (0/false/no/off/empty) to revert to strict opt-in."""
    return os.environ.get("WCB_MULTI_AGENT_DEFAULT", "1").strip().lower() not in (
        "0", "false", "no", "off", "",
    )


def _default_multi_agent_config() -> dict:
    """Capability-only multi_agent config: the sub-agent tools are exposed but
    spawning is neither required nor scored (empty expected_per_turn, no
    aggregate_checker_id). Same shape the runner consumes for native mode."""
    return {
        "enabled": True,
        "native": True,
        "default_allowed_tools": ["Read", "Write", "Edit", "Bash", "Grep", "Glob"],
        "expected_per_turn": {},
    }


def _synthesize_multi_agent_config(task_dir: Path) -> dict:
    """Derive a multi_agent config from prompts.txt "Multi-Agent" turn headers.

    Header form: "--- TURN [T]<n> (..., Multi-Agent) ---" (1-indexed in
    prompts.txt). The openclaw runner exposes 0-indexed turn_index, so we
    subtract 1 to match the expected_per_turn key contract.
    """
    prompts_path = task_dir / "prompts.txt"
    if not prompts_path.is_file():
        return {}
    try:
        text = prompts_path.read_text(encoding="utf-8")
    except OSError:
        return {}
    pattern = re.compile(
        r"^---\s*TURN\s+T?(\d+).*?Multi-Agent.*?---\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    ma_turns = sorted({int(m) - 1 for m in pattern.findall(text)})
    if not ma_turns:
        return {}
    return {
        "enabled": True,
        "default_allowed_tools": ["Read", "Write", "Edit", "Bash", "Grep", "Glob"],
        "expected_per_turn": {
            str(idx): {"min_subagents": 2, "checker_id": f"T{idx}_MA"}
            for idx in ma_turns
        },
        "aggregate_checker_id": "MA_C1",
    }


def _multi_agent_config_from_complex_turns(
    complex_turns: Any,
    num_turns: int | None = None,
    *,
    task_id: str | None = None,
    min_subagents: int = 2,
) -> dict:
    """Derive a multi_agent config from task.yaml ``multi_agent_complex_turns``.

    ``complex_turns`` are 1-indexed turn numbers matching the prompts.txt
    ``--- TURN T<n> ---`` headers; the openclaw runner exposes 0-indexed
    ``turn_index`` (and spawn_tree.jsonl rows carry that), so we subtract 1. The
    returned shape is identical to :func:`_synthesize_multi_agent_config` so
    downstream scoring (``spawn_tree_checks.build_checker_state``) is unchanged —
    only the *source* of the config differs (config key vs. prompts.txt token).

    When ``num_turns`` is known, a configured turn that exceeds the actual turn
    count is kept (so the author's intent is honoured) but logged loudly: such a
    turn can never spawn, so its ``T<idx>_MA`` checker and the ``MA_C1``
    aggregate will fail until task.yaml / prompts.txt / the config agree.
    """
    if not isinstance(complex_turns, (list, tuple)):
        return {}
    idxs: set[int] = set()
    for n in complex_turns:
        try:
            idx = int(n) - 1
        except (TypeError, ValueError):
            continue
        if idx < 0:
            continue
        if num_turns is not None and idx >= num_turns:
            logger.warning(
                "[%s] multi_agent_complex_turns lists turn %s but prompts.txt "
                "has only %d turn(s); turn_index %d can never spawn, so checker "
                "T%d_MA and the MA_C1 aggregate will fail. Align task.yaml "
                "`turns` / prompts.txt / `multi_agent_complex_turns`.",
                task_id or "?", n, num_turns, idx, idx,
            )
        idxs.add(idx)
    if not idxs:
        return {}
    return {
        "enabled": True,
        "default_allowed_tools": ["Read", "Write", "Edit", "Bash", "Grep", "Glob"],
        "expected_per_turn": {
            str(idx): {"min_subagents": min_subagents, "checker_id": f"T{idx}_MA"}
            for idx in sorted(idxs)
        },
        "aggregate_checker_id": "MA_C1",
    }


def _derive_taxonomy_for_native_task(
    task_dir: Path, rubrics: list, attachments: list
) -> tuple[str, str]:
    # Persona-format native tasks (input/<task>/{prompt.txt,rubric.json,persona/,data/,mock_data/})
    # carry no task.toml — the reference trajectory still expects non-empty
    # taxonomy_l1/l2. Optional `<task_dir>/taxonomy.json` overrides; otherwise
    # we derive L1 from the dominant rubric evaluation_target and L2 from the
    # combination of attachment MIME families + per-task mock_data/<api>/ dirs.
    override = task_dir / "taxonomy.json"
    if override.is_file():
        try:
            data = json.loads(override.read_text(encoding="utf-8")) or {}
            l1 = str(data.get("l1") or data.get("taxonomy_l1") or "")
            l2 = str(data.get("l2") or data.get("taxonomy_l2") or "")
            if l1 or l2:
                return l1, l2
        except (json.JSONDecodeError, OSError):
            pass

    targets: dict[str, int] = {}
    for r in rubrics if isinstance(rubrics, list) else []:
        if isinstance(r, dict):
            t = str(r.get("evaluation_target") or "").strip()
            if t:
                targets[t] = targets.get(t, 0) + 1
    dominant_target = max(targets, key=lambda k: targets[k]) if targets else ""
    l1 = {
        "final_answer": "Information Synthesis",
        "workspace_artifact": "File Generation",
        "tool_call_audit": "Tool Use Audit",
    }.get(dominant_target, "Multimodal Reasoning")

    mime_families: set[str] = set()
    for att in attachments if isinstance(attachments, list) else []:
        if isinstance(att, dict):
            mime = str(att.get("mimeType") or "")
            if mime.startswith("image/"):
                mime_families.add("image")
            elif mime in ("text/csv", "application/vnd.ms-excel"):
                mime_families.add("tabular")
            elif mime == "application/pdf":
                mime_families.add("pdf")
            elif mime.startswith(("audio/", "video/")):
                mime_families.add("media")
    api_dirs: list[str] = []
    mock_root = task_dir / "mock_data"
    if mock_root.is_dir():
        api_dirs = sorted(d.name.replace("-api", "") for d in mock_root.iterdir() if d.is_dir())

    parts: list[str] = []
    if "image" in mime_families and "tabular" in mime_families:
        parts.append("receipt_reconciliation")
    elif "image" in mime_families:
        parts.append("image_grounded_analysis")
    elif "tabular" in mime_families:
        parts.append("tabular_data_analysis")
    elif "pdf" in mime_families:
        parts.append("pdf_extraction")
    elif "media" in mime_families:
        parts.append("media_processing")
    else:
        parts.append("text_analysis")
    if api_dirs:
        parts.append("with_" + "_".join(api_dirs[:3]) + "_apis")
    l2 = "__".join(parts) if parts else "general"
    return l1, l2


def _append_workspace_hint(prompt: str, attachments: list[dict]) -> str:
    if not attachments:
        return prompt
    names = sorted({str(a.get("storedAs") or a.get("name") or "") for a in attachments if a})
    names = [n for n in names if n]
    if not names:
        return prompt
    # List every staged input in full. A prior 30-item cap left a literal
    # "... (N more)" truncation marker in the agent's first user message (and
    # thus in the published trajectory), and hid real inputs from the agent.
    listing = "\n".join(f"- {n}" for n in names)
    # Output-location contract pinned to two harness-side enforcers:
    # (a) `collect_output_from_container` snapshots `/root/workspace/`
    # before the agent runs and copies every new-or-modified file out
    # into `task_output/artifacts/`; (b) openclaw's media tools enforce a
    # localRoots allowlist (`assertLocalMediaAllowed` in
    # src/media/local-media-access.ts) that admits `/root/workspace/` and
    # rejects `/tmp/*` plus `/root/<other>/*`. Deliverables written
    # anywhere else are invisible to the grader at collection time and
    # may also fail the image tool at read time.
    #
    # 2026-07-02: wording matters here. The earlier phrasing ("Save EVERY
    # output artifact... will NOT be collected as deliverables") redefined
    # the task's deliverable channel as local files: on Jae_Chandler_01 two
    # different models each read it literally, skipped the Notion/Confluence/
    # Airtable page creation the task's authored tests grade on, and scored
    # 1/22. This footer is a file-collection contract only — it must never
    # steer the agent away from system-of-record actions the task calls for.
    hint = (
        "\n\n---\n"
        "Workspace inputs (already staged on disk at `/root/workspace/home` or `/root/workspace/Home`):\n"
        f"{listing}\n"
        "Any FILE you produce must be saved under `/root/workspace/` — "
        "files written anywhere else (including `/tmp/` and elsewhere "
        "under `/root/`) will NOT be collected. This is a file-collection "
        "rule only; it does not change where the task's deliverables "
        "belong. If the task calls for work in an external system or "
        "service (for example creating or updating pages, records, or "
        "cards through the available APIs), do that work there as asked — "
        "a local file copy does not replace it."
    )
    return prompt + hint


def _load_golden_trajectory(task_dir: Path) -> str:
    """Return the raw JSON text of ``<task_dir>/golden_trajectory.json`` if present.

    Stored verbatim on Task.golden_trajectory (a TEXT column) and emitted into the
    Harbor bundle by write_bundle via ``_trajectory_entries`` (which json-parses
    the string). Produced by system_prompts/generate_golden_trajectory.py.
    """
    p = task_dir / "golden_trajectory.json"
    if p.is_file():
        try:
            return p.read_text(encoding="utf-8")
        except OSError:
            return ""
    return ""


def _load_native_task(task_dir: Path) -> dict:
    # kensei-native task dir: prompt.txt + rubric.json + persona/ + data/ + mock_data/ + gt/.
    # Input artifacts are sourced in PRIORITY order: <task>/persona/home/ first, then
    # <task>/data/ as a fallback (see the input_dir selection below). Whichever is chosen
    # reaches the container via inject_data_into_workspace, which copies it into the
    # workspace at /root/workspace/home, and `attachments` is populated from it for
    # trajectory/harbor/multimodal metadata. (persona/ still supplies SOUL/MEMORY/AGENTS
    # via inject_persona_into_workspace independently of the input-artifact source.)
    turn_messages: list[str] = []
    if (task_dir / "prompt.txt").is_file():
        prompt = (task_dir / "prompt.txt").read_text(encoding="utf-8").strip()
    elif (task_dir / "prompts.txt").is_file():
        # Talos inject-format task: prompts.txt holds the per-turn wake-up script.
        # Turn 0 is the initial prompt; later turns drive the multi-turn silent-
        # injection loop applied at stage boundaries (see inject_director.py).
        from src.utils.inject_director import parse_prompts_file
        turn_messages = parse_prompts_file(task_dir / "prompts.txt")
        prompt = (turn_messages[0] if turn_messages else "").strip()
    elif (task_dir / "PROMPT.md").is_file():
        # Newer authoring format: prompt ships as PROMPT.md (TURN-delimited or plain).
        from src.utils.inject_director import parse_prompts_file
        turn_messages = parse_prompts_file(task_dir / "PROMPT.md")
        prompt = (
            turn_messages[0].strip() if turn_messages
            else (task_dir / "PROMPT.md").read_text(encoding="utf-8").strip()
        )
    else:
        prompt = ""
    try:
        rubrics = json.loads((task_dir / "rubric.json").read_text(encoding="utf-8")) or []
        if isinstance(rubrics, dict):
            rubrics = rubrics.get("rubrics") or []
    except (json.JSONDecodeError, OSError):
        rubrics = []

    parts = task_dir.name.split("__")
    persona = parts[0] if parts and parts[0] else "marcus"

    persona_dir = task_dir / "persona"
    attachments: list[dict] = []
    # Input-artifact source selection, in PRIORITY order:
    #   1. <task>/persona/home/  — preferred when present and non-empty.
    #   2. <task>/data/          — fallback (the dominant layout in this corpus).
    # The chosen dir is staged into the agent workspace at /root/workspace/home by
    # inject_data_into_workspace (the `data_dir` field in the returned task points
    # at it), and `attachments` (storedAs kept under home/ so trajectory media
    # metadata reflects the in-container path) is built from it. An empty
    # persona/home/ (dir with no files) falls through to data/ rather than
    # masking it.
    persona_home = persona_dir / "home"
    data_dir = task_dir / "data"
    if persona_home.is_dir() and any(f.is_file() for f in persona_home.rglob("*")):
        input_dir = persona_home
    elif data_dir.is_dir():
        input_dir = data_dir
    else:
        input_dir = None
    if input_dir is not None:
        for f in sorted(input_dir.rglob("*")):
            if not f.is_file() or f.name.startswith("."):
                continue
            rel = f.relative_to(input_dir).as_posix()
            mime = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
            attachments.append({
                "name": f.name,
                "mimeType": mime,
                "path": str(f.resolve()),
                "size": f.stat().st_size,
                "storedAs": f"home/{rel}",
                "role": "primary",
                "description": "",
            })

    derived_l1, derived_l2 = _derive_taxonomy_for_native_task(task_dir, rubrics, attachments)
    prompt_with_inputs = _append_workspace_hint(prompt, attachments)
    provided_test_code, provided_test_weights = _load_provided_tests(task_dir)
    declared_overrides = _load_native_api_overrides(task_dir)
    checkers_code, conftest_code = _load_checkers_and_conftest(task_dir)
    return {
        "task_id": task_dir.name,
        "prompt": prompt_with_inputs,
        "initial_prompt": prompt_with_inputs,
        "test_code": provided_test_code,
        "test_weights": provided_test_weights,
        # CHECKERS module + conftest for fixture-based suites (state,
        # task_checkers). Shipped into the test sandbox and the bundle.
        "checkers_code": checkers_code,
        "conftest_code": conftest_code,
        "persona": persona,
        "persona_dir": str(persona_dir) if persona_dir.is_dir() else "",
        "data_dir": str(input_dir) if input_dir is not None else "",
        "system_prompt": "",
        "task_description": prompt,
        "rubrics": rubrics,
        "automated_checks": "",
        "difficulty": "medium",
        "l1": derived_l1,
        "l2": derived_l2,
        "task_type": "",
        "modalities": [],
        "multimodal": "false",
        "timeout_seconds": 1800,
        "category": "",
        "file_path": str(task_dir),
        "task_dir": str(task_dir),
        "gt_dir": str(task_dir / "gt") if (task_dir / "gt").is_dir() else "",
        "attachments": attachments,
        "workspace_path": "",
        "skills": "",
        "skills_path": "",
        "warmup": "",
        "env": "",
        "required_apis_declared": declared_overrides["required_apis"],
        "distractor_apis_declared": declared_overrides["distractor_apis"],
        "format": "native",
        # Full per-turn wake-up script for Talos inject-format tasks (empty for
        # single-prompt tasks). run_batch feeds these to the multi-turn runner.
        "turn_messages": turn_messages,
        # Reference golden trajectory (optional). Flows to the Harbor bundle's
        # golden_trajectory.json via write_bundle.
        "golden_trajectory": _load_golden_trajectory(task_dir),
    }


def _load_native_api_overrides(task_dir: Path) -> dict:
    override_path = task_dir / "task.json"
    if override_path.is_file():
        try:
            raw = json.loads(override_path.read_text(encoding="utf-8")) or {}
            if isinstance(raw, dict):
                req = _normalize_declared_api_list(raw, "required_apis", "required_mock_apis")
                dist = _normalize_declared_api_list(raw, "distractor_apis", "distractor_mock_apis")
                return {
                    "required_apis": [] if req == _ABSENT_SENTINEL else req,
                    "distractor_apis": _ABSENT_SENTINEL if dist == _ABSENT_SENTINEL else dist,
                }
        except (json.JSONDecodeError, OSError):
            pass
    return {"required_apis": [], "distractor_apis": _ABSENT_SENTINEL}


_AUTO_SENTINEL = "__AUTO__"
_ABSENT_SENTINEL = "__ABSENT__"


def _normalize_declared_api_list(raw: dict, *keys: str) -> list[str] | str:
    raw_value = None
    found = False
    for k in keys:
        if k in raw:
            found = True
            if raw[k] is not None:
                raw_value = raw[k]
                break
    if not found:
        return _ABSENT_SENTINEL
    if raw_value is None:
        return []
    if isinstance(raw_value, str) and raw_value.strip().lower() == "auto":
        return _AUTO_SENTINEL
    if isinstance(raw_value, str):
        raw_value = [raw_value]
    out: set[str] = set()
    for item in raw_value:
        s = str(item).strip()
        if not s:
            continue
        if not s.endswith("-api"):
            s = f"{s}-api"
        out.add(s)
    return sorted(out)


_TEXT_MODALITIES = {"text", "txt", "plain"}


def _normalize_modalities(raw: dict) -> list[str]:
    v = raw.get("modalities")
    if v is None:
        return []
    if isinstance(v, str):
        v = [v]
    out: list[str] = []
    seen: set[str] = set()
    for item in v:
        s = str(item).strip().lower()
        if not s or s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out


_YAML_METADATA_KEYS = frozenset({
    "difficulty",
    "modalities",
    "l1", "taxonomy_l1",
    "l2", "taxonomy_l2",
    "task_type", "category",
    "required_apis", "required_mock_apis",
    "distractor_apis", "distractor_mock_apis",
    "multi_agent_complex_turns",
})


def _overlay_yaml_metadata(base: dict, yaml_path: Path) -> dict:
    raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        return base

    if "difficulty" in raw and raw["difficulty"] is not None:
        base["difficulty"] = str(raw["difficulty"])

    modalities = _normalize_modalities(raw)
    if modalities:
        base["modalities"] = modalities
        base["multimodal"] = "true" if any(m not in _TEXT_MODALITIES for m in modalities) else "false"

    l1 = raw.get("l1") or raw.get("taxonomy_l1")
    if l1:
        base["l1"] = str(l1)
    l2 = raw.get("l2") or raw.get("taxonomy_l2")
    if l2:
        base["l2"] = str(l2)

    task_type = raw.get("task_type") or raw.get("category")
    if task_type:
        base["task_type"] = str(task_type)
        base["category"] = str(task_type)

    required = _normalize_declared_api_list(raw, "required_apis", "required_mock_apis")
    if required != _ABSENT_SENTINEL:
        base["required_apis_declared"] = required
    distractor = _normalize_declared_api_list(raw, "distractor_apis", "distractor_mock_apis")
    if distractor != _ABSENT_SENTINEL:
        base["distractor_apis_declared"] = distractor

    # 1-indexed turn numbers the author marked as needing sub-agent fan-out.
    # _attach_drift_script turns this into the multi_agent_config / scoring
    # checkers (see _multi_agent_config_from_complex_turns).
    if raw.get("multi_agent_complex_turns") is not None:
        base["multi_agent_complex_turns"] = raw.get("multi_agent_complex_turns")

    ignored = [k for k in raw.keys() if k not in _YAML_METADATA_KEYS]
    if ignored:
        base.setdefault("_yaml_ignored_keys", []).extend(sorted(ignored))

    base["format"] = "native+yaml"
    return base
