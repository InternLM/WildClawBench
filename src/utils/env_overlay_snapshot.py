"""Stage the post-overlay mock environment to a destination directory.

The mock stack (src/utils/mock_stack.py:start_mock_stack) starts the
kensei3-mocks:v1 container with the entire environment/<api>/ baseline at
/opt/mocks/<api>/, then read-only bind-mounts each per-task overlay file at
/opt/mocks/<api>/<filename>:ro (mock_stack.py:343-344). The agent talks to
those APIs over HTTP and never sees the files on disk -- but because the
mounts are :ro, the container's view of /opt/mocks/ is deterministically
equal to the host-side merge: baseline + overlays where overlays win on
filename collision.

This module reproduces that merge on the host so we can snapshot the
"after overlay" state into output/<backend>/<task>/data/environment/ and
have it round-trip into output_bundle/<task>/data/environment/ via the
existing copytree in script/repackage_to_bundle.py:783. Both run_batch.py
(auto path) and repackage_to_bundle.py (manual --all) end up with byte-
identical data/environment/<api>/** trees -- satisfying the convergence
invariant in script/AGENTS.md ("run.sh and python3 eval/run_batch.py
should converge on identical artifacts").

Stdlib only by design: repackage_to_bundle.py is stdlib-only per
script/AGENTS.md and reads the manifest this module writes; keeping this
module stdlib-only means we could later move the dedup logic across the
boundary without dependency churn.

The dict that drives the overlay (task["mock_overlays"]) is built in
eval/run_batch.py:_resolve_task_apis (lines 404-418) directly from
input/<task>/mock_data/<api>/* and is what start_mock_stack receives.
That makes it the authoritative source of truth for "what files were
overlaid for this task".
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Iterable

MANIFEST_FILENAME = "_overlay_manifest.json"

# Top-level subdirs under environment/ that this module must NEVER snapshot
# into output/<backend>/<task>/data/environment/. Lock-step with the bundler
# ignore_patterns at script/repackage_to_bundle.py:1864-1881 (b62) so the
# --stage-output-data parity contract (b53) holds end-to-end:
#   - "scripts": repo dev-tooling (audit_data_formats.py, migrate_csv_to_json.py,
#     wiring_report.py, endpoint_run.log, format_audit.json, wiring_report.json)
#     -- engineering scaffolding, never for graded recipients.
# Filename-glob patterns inside per-api copies (e.g. *.pyc, __pycache__) are
# handled separately via shutil.ignore_patterns(...) on the copytree call below.
_SKIP_TOPLEVEL_NAMES: frozenset[str] = frozenset({"scripts", "__pycache__"})

# Top-level subdir name PREFIXES under environment/ that must NEVER snapshot
# (fnmatch-style globs against the leaf name).
_SKIP_TOPLEVEL_PREFIXES: tuple[str, ...] = ("self-improving-agent-",)


def _is_skipped_toplevel(name: str) -> bool:
    if name in _SKIP_TOPLEVEL_NAMES:
        return True
    return any(name.startswith(p) for p in _SKIP_TOPLEVEL_PREFIXES)


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _iter_api_dirs(env_baseline: Path) -> Iterable[Path]:
    if not env_baseline.is_dir():
        return []
    return sorted(
        p for p in env_baseline.iterdir()
        if p.is_dir() and not _is_skipped_toplevel(p.name)
    )


def _per_api_copytree_ignore(api_name: str, api_root: Path):
    """Path-aware ignore for a single api / top-level env subdir copy.

    Build artifacts (__pycache__, *.pyc) are stripped at any depth -- they
    are never legitimate content for the bundle. The "self-improving-agent-*"
    filter only applies when the iteration is at <skills>/ root (it's an
    internal R&D meta-skill, never under api dirs anyway). The "scripts"
    name is NEVER stripped here -- shipping `<skill>/scripts/` is the
    common case for connector skills. The top-level `environment/scripts/`
    dir is already prevented from being iterated via _SKIP_TOPLEVEL_NAMES.
    """
    root = api_root.resolve()

    def _ignore(src_dir: str, names):
        src = Path(src_dir).resolve()
        out: set[str] = set()
        for n in names:
            if n == "__pycache__" or n.endswith(".pyc"):
                out.add(n)
            elif api_name == "skills" and src == root and n.startswith("self-improving-agent-"):
                out.add(n)
        return out

    return _ignore


def stage_environment_with_overlays(
    env_baseline: Path,
    overlays: dict | None,
    dest: Path,
    *,
    write_manifest: bool = True,
) -> dict:
    """Mirror env_baseline/<api>/** into dest/<api>/** with overlays applied.

    Args:
        env_baseline: <repo>/environment/ (config.environment_dir).
        overlays: task["mock_overlays"] = {api_name: {filename: host_path_str}}
                  where host_path_str is an absolute path under
                  input/<task>/mock_data/<api>/. Same dict that
                  start_mock_stack() received as -v ...:/opt/mocks/<api>/<file>:ro.
                  May be None or empty -- baseline-only mirror still happens.
        dest: target dir (e.g. output/<backend>/<task>/data/environment/).
        write_manifest: when True, write {MANIFEST_FILENAME} alongside the
                        api dirs recording per-overlay-file metadata so
                        repackage_to_bundle.py can verify provenance later.
                        Callers writing into output/ should set True;
                        callers writing into a published bundle should set
                        False (per user contract: manifest stays in output/
                        only, never leaks into deliverable bundle).

    Returns:
        Manifest dict (always returned, even when not written to disk) of
        shape {"baseline_root": str, "apis": {api: {"files": {filename: {
        "sha256": str, "source_relpath": str, "size": int}}}}}. Suitable
        for json.dumps with sort_keys=True.

    Behavior:
        - dest is created if missing.
        - dest/<api>/ is wiped+recopied from baseline first to guarantee
          no stale files survive between runs. This matches the container
          semantics: each `docker run` starts from a fresh /opt/mocks/ image
          layer, so the snapshot must too. Without the wipe, files that
          appeared in a previous task's overlay but not this task's would
          linger as ghosts in /opt/mocks/<api>/ in the snapshot.
        - For each (api, {filename: host_path}) in overlays, the file at
          dest/<api>/<filename> is replaced by host_path's contents.
        - Files that exist in baseline but not in any overlay are kept
          (this is the container's view: baseline shows through where the
          overlay didn't mount anything).
        - Overlay files NOT present in baseline are still written (matches
          container behavior: docker -v creates the target path if needed
          for files, which is the case for novel files an overlay introduces).
    """
    overlays = overlays or {}
    dest.mkdir(parents=True, exist_ok=True)

    manifest: dict = {
        "baseline_root": str(env_baseline),
        "apis": {},
    }

    # Pre-pass: figure out which api dirs need to exist in dest. Union of
    # baseline api dirs + any api the overlay mentions (overlay may add an
    # api dir that's not in baseline -- unusual but matches container's
    # ability to mount into a fresh path).
    baseline_apis = {p.name: p for p in _iter_api_dirs(env_baseline)}
    overlay_apis = {
        api for api in overlays.keys()
        if isinstance(api, str) and not _is_skipped_toplevel(api)
    }
    all_apis = sorted(set(baseline_apis.keys()) | overlay_apis)

    for api in all_apis:
        api_dest = dest / api
        # Wipe-and-recopy: see docstring -- guards against stale files
        # surviving from a prior run that overlaid a file this run does not.
        if api_dest.exists():
            shutil.rmtree(api_dest)

        baseline_api_dir = baseline_apis.get(api)
        if baseline_api_dir is not None:
            shutil.copytree(
                baseline_api_dir,
                api_dest,
                ignore=_per_api_copytree_ignore(api, baseline_api_dir),
            )
        else:
            api_dest.mkdir(parents=True, exist_ok=True)

        api_overlays = overlays.get(api) or {}
        if not isinstance(api_overlays, dict):
            api_overlays = {}

        files_meta: dict = {}
        for filename, host_path_str in sorted(api_overlays.items()):
            if not isinstance(filename, str) or not isinstance(host_path_str, str):
                continue
            host_path = Path(host_path_str)
            if not host_path.is_file():
                # Mirror mock_stack behavior: a broken overlay path would
                # have made the docker run fail at mount time. Here we
                # tolerate it (the run already completed) but record nothing
                # so the manifest doesn't lie about what was applied.
                continue
            target = api_dest / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(host_path, target)
            try:
                stat = target.stat()
                files_meta[filename] = {
                    "sha256": _sha256_file(target),
                    "source_path": str(host_path),
                    "size": int(stat.st_size),
                }
            except OSError:
                files_meta[filename] = {
                    "sha256": "",
                    "source_path": str(host_path),
                    "size": 0,
                }

        manifest["apis"][api] = {"files": files_meta}

    if write_manifest:
        manifest_path = dest / MANIFEST_FILENAME
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    return manifest


def read_overlay_manifest(env_dir: Path) -> dict | None:
    """Read {MANIFEST_FILENAME} from env_dir; return None if absent/malformed.

    Provided as a single read path so any future consumer (test harness,
    audit script, regrade) doesn't reinvent the parse + tolerate-missing
    pattern. Currently unused by the bundler (it inherits the staged tree
    via copytree and intentionally never sees the manifest -- see
    script/repackage_to_bundle.py:788 ignore_patterns).
    """
    p = env_dir / MANIFEST_FILENAME
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
