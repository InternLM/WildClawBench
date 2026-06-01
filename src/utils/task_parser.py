from __future__ import annotations

import json
import mimetypes
import re
from pathlib import Path
from typing import Any, Optional
from dotenv import load_dotenv

import yaml

load_dotenv()
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
    """Load a task from a .md / .yaml file or a native task directory.

    - .md          -> parse_task_md (unchanged fork behavior), normalized superset
    - .yaml/.yml   -> _load_yaml_task
    - directory    -> task.yaml|task.yml|task.md inside, else native
                      (prompt.txt + rubric.json) layout
    """
    p = Path(path)
    if p.is_dir():
        for candidate in ("task.yaml", "task.yml", "task.md"):
            f = p / candidate
            if f.is_file():
                return load_task(f)
        if (p / "prompt.txt").is_file() and (p / "rubric.json").is_file():
            return _load_native_task(p)
        raise FileNotFoundError(f"No task file found in {p}")
    suffix = p.suffix.lower()
    if suffix in (".yaml", ".yml"):
        return _load_yaml_task(p)
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
        return base
    raise ValueError(f"Unsupported task file format: {p.suffix}")


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


def _load_native_task(task_dir: Path) -> dict:
    # kensei-native task dir: prompt.txt + rubric.json + persona/ + data/ + mock_data/ + gt/.
    # workspace_path is left empty here; run_batch stages a workspace from
    # `attachments` so task solutions/tests under data/ are never exposed.
    prompt = (task_dir / "prompt.txt").read_text(encoding="utf-8").strip()
    try:
        rubrics = json.loads((task_dir / "rubric.json").read_text(encoding="utf-8")) or []
        if isinstance(rubrics, dict):
            rubrics = rubrics.get("rubrics") or []
    except (json.JSONDecodeError, OSError):
        rubrics = []

    parts = task_dir.name.split("__")
    persona = parts[0] if parts and parts[0] else "marcus"

    attachments: list[dict] = []
    data_dir = task_dir / "data"
    if data_dir.is_dir():
        for f in sorted(data_dir.rglob("*")):
            if not f.is_file() or f.name.startswith("."):
                continue
            # never expose graders/solutions/bundle-scaffolding to the agent workspace
            rel = f.relative_to(data_dir).as_posix()
            if rel.startswith(("tests/", "solution/", "environment/")) or rel in ("task.toml", "instruction.md"):
                continue
            mime = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
            attachments.append({
                "name": f.name,
                "mimeType": mime,
                "path": str(f.resolve()),
                "size": f.stat().st_size,
                "storedAs": f.name,
                "role": "primary",
                "description": "",
            })

    persona_dir = task_dir / "persona"
    derived_l1, derived_l2 = _derive_taxonomy_for_native_task(task_dir, rubrics, attachments)
    return {
        "task_id": task_dir.name,
        "prompt": prompt,
        "initial_prompt": prompt,
        "persona": persona,
        "persona_dir": str(persona_dir) if persona_dir.is_dir() else "",
        "system_prompt": "",
        "task_description": prompt[:400],
        "rubrics": rubrics,
        "automated_checks": "",
        "difficulty": "medium",
        "l1": derived_l1,
        "l2": derived_l2,
        "task_type": "",
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
        "format": "native",
    }


def _load_yaml_task(path: Path) -> dict:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    task_dir = path.parent
    task_id = str(raw.get("task_id") or task_dir.name)
    attachments = _load_attachments_yaml(raw, task_dir)
    prompt = str(raw.get("initial_prompt") or raw.get("prompt") or "")
    return {
        "task_id": task_id,
        "prompt": prompt,
        "initial_prompt": prompt,
        "persona": str(raw.get("persona") or "marcus"),
        "persona_dir": "",
        "system_prompt": str(raw.get("system_prompt") or ""),
        "task_description": str(raw.get("task_description") or ""),
        "rubrics": raw.get("rubrics") or [],
        "automated_checks": str(raw.get("automated_checks") or ""),
        "difficulty": str(raw.get("difficulty") or "medium"),
        "l1": str(raw.get("l1") or raw.get("taxonomy_l1") or ""),
        "l2": str(raw.get("l2") or raw.get("taxonomy_l2") or ""),
        "task_type": str(raw.get("task_type") or ""),
        "timeout_seconds": int(raw.get("timeout_seconds") or 1800),
        "category": str(raw.get("category") or ""),
        "file_path": str(path),
        "task_dir": str(task_dir),
        "gt_dir": str(task_dir / "gt") if (task_dir / "gt").is_dir() else "",
        "attachments": attachments,
        "workspace_path": "",
        "skills": str(raw.get("skills") or ""),
        "skills_path": "",
        "warmup": str(raw.get("warmup") or ""),
        "env": str(raw.get("env") or ""),
        "format": "yaml",
    }


def _load_attachments_yaml(raw: dict, task_dir: Path) -> list[dict]:
    att_dir = task_dir / "attachments"
    declared: list = raw.get("attachments") or []
    attachments: list[dict] = []
    for spec in declared:
        if isinstance(spec, str):
            spec = {"path": spec}
        p = Path(spec["path"])
        if not p.is_absolute():
            p = (att_dir / spec["path"]).resolve()
        if not p.is_file():
            continue
        mime = spec.get("mimeType") or mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        attachments.append({
            "name": spec.get("name") or p.name,
            "mimeType": mime,
            "path": str(p),
            "size": p.stat().st_size,
            "storedAs": p.name,
                "role": spec.get("role") or "primary",
            "description": spec.get("description") or "",
        })
    if not declared and att_dir.is_dir():
        for f in sorted(att_dir.iterdir()):
            if not f.is_file():
                continue
            mime = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
            attachments.append({
                "name": f.name,
                "mimeType": mime,
                "path": str(f),
                "size": f.stat().st_size,
                "storedAs": f.name,
                "role": "primary",
                "description": "",
            })
    return attachments
