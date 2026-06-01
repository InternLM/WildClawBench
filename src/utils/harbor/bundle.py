"""Harbor bundle writer.

Assembles every artifact Harbor expects under `<out_dir>/`. Port of
`action_export_to_harbor` (kensei2.py:2638) without S3 upload.

Layout (relative to `out_dir`):
  prompt.txt
  rubric.json
  golden_trajectory.json
  data/instruction.md
  data/task.toml
  data/environment/...                  (copied verbatim from config.environment_dir)
  data/environment/Dockerfile
  data/environment/docker-compose.yaml
  data/tests/test.sh
  data/tests/test_outputs.py
  data/tests/test_weights.json
  data/solution/solve.sh
  trajectories/<model>/run_<N>/output.json
  trajectories/<model>/run_<N>/task_output/logs/verifier/reward.txt
  trajectories/<model>/run_<N>/task_output/logs/verifier/ctrf.json
  trajectories/<model>/pass_summary.json
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set

from src.utils.config import Config
from src.utils.skills_inference import compute_distractor_skills, infer_required_apis
from src.utils.store import Store, Task
from .compose import discover_services, generate_harbor_compose
from .ctrf import build_ctrf, compute_test_reward
from .dockerfile import generate_harbor_dockerfile
from .solve_sh import generate_harbor_solve_sh
from .task_toml import build_task_toml
from .test_sh import generate_harbor_test_sh


_MODEL_DIRS = ("claude", "gpt")
_API_REGEX = re.compile(r"\b([a-z][a-z0-9-]*-api)\b")
_KEEP_TOP_LEVEL = {"API_DOCUMENTATION.md", "tracking_middleware.py", "sqlite_mcp_server.db", "skills"}


def _discover_used_apis(task: Task, task_dir: Optional[Path], env_dir: Path) -> Set[str]:
    if not env_dir.is_dir():
        return set()
    available = {
        d.name for d in env_dir.iterdir()
        if d.is_dir() and (d / "service.toml").exists()
    }
    used: Set[str] = set()
    if task_dir is not None:
        md = Path(task_dir) / "mock_data"
        if md.is_dir():
            used.update(d.name for d in md.iterdir() if d.is_dir())
    prompt = task.initial_prompt or task.seed_prompt or ""
    used.update(infer_required_apis(prompt))
    text = (prompt + " " + (task.rubrics_json or "")).lower()
    used.update(_API_REGEX.findall(text))
    return used & available


def _safe_json_parse(value: Any) -> Any:
    if value is None or value == "":
        return None
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return None
    return None


def _transform_rubrics_for_export(raw: Any) -> List[dict]:
    """Port of `_transform_rubrics_for_export` (kensei2.py:3177)."""
    parsed = _safe_json_parse(raw) or []
    if not isinstance(parsed, list):
        return []
    out: List[dict] = []
    for idx, item in enumerate(parsed):
        if not isinstance(item, dict):
            continue
        out.append({
            "criterion": item.get("label") or item.get("criterion") or "",
            "is_positive": bool(item.get("is_positive", True)),
            "type": item.get("type") or "objective",
            "evaluation_target": item.get("evaluation_target") or "state change",
            "importance": item.get("importance") or "important",
            "score": item.get("score") or 0,
            "number": f"R{idx + 1}",
        })
    return out


def _trajectory_entries(traj_blob: Any) -> List[dict]:
    parsed = _safe_json_parse(traj_blob)
    if isinstance(parsed, list):
        return [e for e in parsed if isinstance(e, dict)]
    if isinstance(parsed, dict):
        return [parsed]
    return []


def _collect_env_vars(env_dir: Path) -> Dict[str, str]:
    services = discover_services(env_dir)
    env_vars: Dict[str, str] = {}
    for svc in services:
        env_var_name = svc.get("env_var_name")
        if not env_var_name:
            continue
        env_vars[env_var_name] = f"http://{svc['name']}:{svc['port']}"
    return env_vars


def _dependency_tags(task: Task) -> List[str]:
    tags = [t for t in (task.l1, task.l2) if t]
    return tags


def _dimensions(task: Task, attachments_present: bool) -> Dict[str, str]:
    return {
        "complex": "medium",
        "long_horizon": "false",
        "objective": "true",
        "multimodal": "true" if attachments_present else "false",
        "cross_modal_cross_api": "false",
        "asset_complexity": "low",
    }


def write_bundle(
    task: Task,
    out_dir: Path,
    store: Store,
    config: Config,
    trajectories_by_model: Optional[Mapping[str, List[dict]]] = None,
    attachments: Optional[Iterable[Mapping]] = None,
    pass_at_k: Optional[int] = None,
    task_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Materialize a Harbor bundle on disk and return a manifest dict.

    `trajectories_by_model` maps model_type (e.g. 'claude', 'gpt') to a list
    of trajectory dicts (one per pod / run). When omitted the writer falls
    back to `task.golden_trajectory` or stored sandbox trajectories.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    attachments_list = list(attachments or [])

    used_apis: Set[str] = _discover_used_apis(task, task_dir, config.environment_dir)
    all_services = discover_services(config.environment_dir)
    filtered_services = (
        [s for s in all_services if s.get("name") in used_apis]
        if used_apis else all_services
    )
    env_vars: Dict[str, str] = {}
    for svc in filtered_services:
        env_var_name = svc.get("env_var_name")
        if env_var_name:
            env_vars[env_var_name] = f"http://{svc['name']}:{svc['port']}"

    prompt_text = task.initial_prompt or task.seed_prompt or ""
    (out_dir / "prompt.txt").write_text(prompt_text, encoding="utf-8")

    rubric_list = _transform_rubrics_for_export(task.rubrics_json)
    (out_dir / "rubric.json").write_text(
        json.dumps(rubric_list, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    golden_entries = _trajectory_entries(task.golden_trajectory)
    golden_doc: Any = golden_entries[0] if golden_entries else {}
    (out_dir / "golden_trajectory.json").write_text(
        json.dumps(golden_doc, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    data_dir = out_dir / "data"
    (data_dir / "tests").mkdir(parents=True, exist_ok=True)
    (data_dir / "solution").mkdir(parents=True, exist_ok=True)

    (data_dir / "instruction.md").write_text(prompt_text, encoding="utf-8")

    # `used_apis` (line 158) is the canonical required-API set computed via
    # `_discover_used_apis(task, task_dir, env_dir)` which fuses prompt-keyword
    # matches with the task's mock_data/<api>/ overlay dirs. The bare
    # `infer_required_apis(prompt)` call returns [] for persona-format tasks
    # whose prompt has no literal API names, which silently wrote
    # `required_skills = []` to data/task.toml — the b31 bug class.
    required = sorted(used_apis) if used_apis else list(infer_required_apis(prompt_text))
    task_id_for_distractor = task.task_id or (str(task.id) if task.id else "")
    distractor = list(compute_distractor_skills(required, task_id_for_distractor))
    required_skills = [f"{name}-connector" for name in required]
    distractor_skills = [f"{name}-connector" for name in distractor]

    # Per-service healthcheck. The default `curl -f http://localhost:8000/health`
    # hits a stub port no real service listens on, masking liveness failures
    # in CI. Chain one curl per filtered service so the mocks container is
    # only "healthy" once every required API is actually serving traffic.
    healthcheck_cmd = " && ".join(
        f"curl -f http://localhost:{svc['port']}/health"
        for svc in filtered_services
        if svc.get("port")
    ) or None

    toml_text = build_task_toml(
        task=task,
        required_skills=required_skills,
        distractor_skills=distractor_skills,
        env_vars=env_vars,
        dependency_tags=_dependency_tags(task),
        dimensions=_dimensions(task, bool(attachments_list)),
        verifier_env=env_vars,
        solution_env=env_vars,
        pass_at_k=pass_at_k,
        healthcheck_command=healthcheck_cmd,
    )
    (data_dir / "task.toml").write_text(toml_text, encoding="utf-8")

    env_out = data_dir / "environment"
    if env_out.exists():
        shutil.rmtree(env_out)
    env_out.mkdir(parents=True, exist_ok=True)
    _bundle_ignore = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo")
    # `skills/` ships 100+ connector skills by default. Filtering to the union of
    # required + distractor API connectors + the 3 multimodal helpers
    # (video-frames, pdf-extract, audio-extract) cuts ~95% of the bundle size
    # without losing anything an LLM agent could legitimately use for this task.
    keep_skill_names: Set[str] = {f"{name}-connector" for name in (set(required) | set(distractor))}
    keep_skill_names.update({"video-frames", "pdf-extract", "audio-extract", "self-improving"})
    def _copy_skills_filtered(src: Path, dst: Path) -> None:
        dst.mkdir(parents=True, exist_ok=True)
        for child in src.iterdir():
            if child.is_dir() and (not keep_skill_names or child.name in keep_skill_names):
                shutil.copytree(child, dst / child.name, ignore=_bundle_ignore)
            elif child.is_file():
                shutil.copy2(child, dst / child.name)
    if config.environment_dir.is_dir():
        if used_apis:
            for item in config.environment_dir.iterdir():
                if item.is_dir():
                    if item.name == "skills":
                        _copy_skills_filtered(item, env_out / item.name)
                    elif item.name in used_apis or item.name in _KEEP_TOP_LEVEL:
                        shutil.copytree(item, env_out / item.name, ignore=_bundle_ignore)
                elif item.name in _KEEP_TOP_LEVEL:
                    shutil.copy2(item, env_out / item.name)
        else:
            for item in config.environment_dir.iterdir():
                if item.is_dir():
                    if item.name == "skills":
                        _copy_skills_filtered(item, env_out / item.name)
                    else:
                        shutil.copytree(item, env_out / item.name, ignore=_bundle_ignore)
                else:
                    shutil.copy2(item, env_out / item.name)

    overlays = task.extra.get("mock_data_overlays", {}) if isinstance(task.extra, dict) else {}
    if not overlays and task_dir is not None:
        td = Path(task_dir) / "mock_data"
        if td.is_dir():
            overlays = {
                api_dir.name: {
                    p.name: str(p.resolve())
                    for p in api_dir.iterdir() if p.is_file()
                }
                for api_dir in sorted(td.iterdir())
                if api_dir.is_dir() and any(p.is_file() for p in api_dir.iterdir())
            }
    if isinstance(overlays, dict):
        for api_name, files_map in overlays.items():
            if not isinstance(files_map, dict):
                continue
            api_dst = env_out / api_name
            api_dst.mkdir(parents=True, exist_ok=True)
            for fname, src in files_map.items():
                try:
                    shutil.copy2(src, api_dst / fname)
                except Exception:
                    pass

    (env_out / "Dockerfile").write_text(generate_harbor_dockerfile(), encoding="utf-8")
    (env_out / "docker-compose.yaml").write_text(
        generate_harbor_compose(config.environment_dir, services=filtered_services),
        encoding="utf-8",
    )

    (data_dir / "tests" / "test.sh").write_text(generate_harbor_test_sh(), encoding="utf-8")
    (data_dir / "tests" / "test_outputs.py").write_text(task.test_code or "", encoding="utf-8")
    test_weights_text = task.test_weights or "{}"
    (data_dir / "tests" / "test_weights.json").write_text(test_weights_text, encoding="utf-8")

    solve_sh = generate_harbor_solve_sh(env_vars)
    (data_dir / "solution" / "solve.sh").write_text(solve_sh, encoding="utf-8")

    if task_dir is not None:
        task_dir = Path(task_dir)
        for sub in ("tests", "solution"):
            src_sub = task_dir / sub
            if not src_sub.is_dir():
                continue
            dst_sub = data_dir / sub
            for item in src_sub.iterdir():
                if item.name.startswith("."):
                    continue
                dst = dst_sub / item.name
                if item.is_dir():
                    shutil.copytree(item, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dst)

    if trajectories_by_model is None:
        trajectories_by_model = {}
        for model in _MODEL_DIRS:
            field_name = f"{model}_trajectory"
            blob = task.extra.get(field_name) if isinstance(task.extra, dict) else None
            entries = _trajectory_entries(blob)
            if entries:
                trajectories_by_model[model] = entries

    test_results_by_sandbox: Dict[int, List[dict]] = {}
    try:
        results = store.list_test_results(task.id) if task.id else []
    except Exception:
        results = []
    for row in results:
        sid = row.get("sandbox_id")
        if sid is None:
            continue
        test_results_by_sandbox.setdefault(int(sid), []).append(row)

    pass_summaries: Dict[str, Any] = {}

    for model, entries in (trajectories_by_model or {}).items():
        model_dir = out_dir / "trajectories" / model
        model_dir.mkdir(parents=True, exist_ok=True)
        per_run: List[dict] = []

        for run_index, entry in enumerate(entries, start=1):
            run_dir = model_dir / f"run_{run_index}"
            run_dir.mkdir(parents=True, exist_ok=True)

            clean_entry = (
                {k: v for k, v in entry.items() if k != "__test_result__"}
                if isinstance(entry, dict) else entry
            )
            (run_dir / "output.json").write_text(
                json.dumps(clean_entry, indent=2, ensure_ascii=False), encoding="utf-8"
            )

            tr = entry.get("__test_result__") if isinstance(entry, dict) else None
            tests_total = int((tr or {}).get("tests_total", 0))
            tests_passed = int((tr or {}).get("tests_passed", 0))
            tests_failed = int((tr or {}).get("tests_failed", 0))
            tests_errored = int((tr or {}).get("tests_errored", 0))
            test_scores = (tr or {}).get("test_scores", "")
            test_output = (tr or {}).get("test_output", "")
            test_code = (tr or {}).get("test_code", task.test_code or "")

            reward = compute_test_reward(
                test_weights_json=test_weights_text,
                test_scores_json=test_scores,
                tests_total=tests_total,
                tests_passed=tests_passed,
                test_output=test_output,
                test_code=test_code,
            )

            if run_index <= 8:
                verifier_dir = run_dir / "task_output" / "logs" / "verifier"
                verifier_dir.mkdir(parents=True, exist_ok=True)
                (verifier_dir / "reward.txt").write_text(f"{reward:.6f}\n", encoding="utf-8")
                ctrf = build_ctrf(
                    tests_total=tests_total,
                    tests_passed=tests_passed,
                    tests_failed=tests_failed,
                    tests_errored=tests_errored,
                    test_scores_json=test_scores,
                )
                (verifier_dir / "ctrf.json").write_text(
                    json.dumps(ctrf, indent=2, ensure_ascii=False), encoding="utf-8"
                )

            per_run.append({
                "run_index": run_index,
                "tests_total": tests_total,
                "tests_passed": tests_passed,
                "tests_failed": tests_failed,
                "reward": reward,
            })

        avg_reward = (
            sum(r["reward"] for r in per_run) / len(per_run) if per_run else 0.0
        )
        summary = {
            "model": model,
            "runs": len(per_run),
            "average_reward": avg_reward,
            "per_run": per_run,
        }
        (model_dir / "pass_summary.json").write_text(
            json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        pass_summaries[model] = summary

    return {
        "out_dir": str(out_dir),
        "models": list((trajectories_by_model or {}).keys()),
        "pass_summaries": pass_summaries,
        "required_skills": required_skills,
        "distractor_skills": distractor_skills,
        "env_vars": env_vars,
    }
