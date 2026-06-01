"""Scan the environment/ tree for mock-API service metadata.

Reads each `<name>-api/service.toml`, the global API_DOCUMENTATION.md, and a
compact CSV/JSON data snapshot to ground the LLM's assertions in real IDs/values.

Ported from kensei2/models/kensei2_sandbox.py (lines 38-163, 976-996).
Gracefully degrades to empty results when the environment tree is missing
(Phase B step 10 may not yet be populated in the fork).
"""

from __future__ import annotations

import csv as _csv
import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional

_logger = logging.getLogger(__name__)

ServiceInfo = Dict[str, object]  # {"name": str, "env_var": str, "port": int}


def _parse_service_toml(path: str) -> Optional[dict]:
    """Minimal TOML parser for service.toml.

    We intentionally avoid pulling tomllib/tomli for a 4-field file. Returns
    None when the required `service.name` is missing.
    """
    result = {
        "name": "", "port": 0, "env_var_name": "", "healthcheck_path": "/health",
    }
    key_map = {
        "service.name": "name",
        "service.port": "port",
        "service.env_var_name": "env_var_name",
        "service.healthcheck_path": "healthcheck_path",
    }
    section = ""
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("[") and line.endswith("]"):
                    section = line[1:-1].strip()
                    continue
                if "=" in line and not line.startswith("#"):
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    full_key = "%s.%s" % (section, key) if section else key
                    if full_key in key_map:
                        mapped = key_map[full_key]
                        if mapped == "port":
                            try:
                                val = int(val)
                            except ValueError:
                                val = 0
                        result[mapped] = val
    except OSError:
        return None
    return result if result["name"] else None


def read_services(env_dir: Path | str | None) -> Dict[str, ServiceInfo]:
    """Discover every `<name>-api/service.toml` under env_dir.

    Returns `{api_name: {env_var, port}}`. Empty dict if env_dir is missing,
    not a directory, or has no service.toml files — caller must treat this as
    a non-API task (no <SERVICE>_URL wrapper constants, no L8/L24/L26 lint).
    """
    if not env_dir:
        return {}
    env_path = Path(env_dir)
    if not env_path.is_dir():
        return {}
    services: Dict[str, ServiceInfo] = {}
    for entry in sorted(os.listdir(env_path)):
        svc_dir = env_path / entry
        toml_path = svc_dir / "service.toml"
        if svc_dir.is_dir() and toml_path.is_file():
            meta = _parse_service_toml(str(toml_path))
            if meta:
                services[meta["name"]] = {
                    "env_var": meta["env_var_name"],
                    "port": meta["port"],
                }
    return services


def read_api_docs(env_dir: Path | str | None, max_chars: int = 30000) -> str:
    """Read environment/API_DOCUMENTATION.md, truncated to max_chars."""
    if not env_dir:
        return ""
    path = Path(env_dir) / "API_DOCUMENTATION.md"
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n... [truncated]"
    return text


@lru_cache(maxsize=4)
def _cached_snapshot(env_dir_str: str, max_rows: int, max_services: int) -> str:
    return _collect_mock_data_snapshot_impl(env_dir_str, max_rows, max_services)


def collect_mock_data_snapshot(
    env_dir: Path | str | None,
    *,
    max_rows: int = 3,
    max_services: int = 10,
) -> str:
    """Compact text snapshot of real entity IDs/field values for grounding.

    Cached per env_dir — the snapshot is deterministic and reading 101 service
    dirs per task is wasteful. Returns "" when env_dir is missing.
    """
    if not env_dir:
        return ""
    env_path = Path(env_dir)
    if not env_path.is_dir():
        return ""
    return _cached_snapshot(str(env_path), max_rows, max_services)


def _collect_mock_data_snapshot_impl(env_dir_str: str, max_rows: int, max_services: int) -> str:
    env_dir = env_dir_str
    snapshot_parts = []
    service_count = 0

    for entry in sorted(os.listdir(env_dir)):
        svc_dir = os.path.join(env_dir, entry)
        if not os.path.isdir(svc_dir) or entry in ("skills", "__pycache__"):
            continue
        toml_path = os.path.join(svc_dir, "service.toml")
        if not os.path.isfile(toml_path):
            continue

        service_count += 1
        if service_count > max_services:
            break

        svc_lines = ["### %s" % entry]
        file_count = 0

        for fname in sorted(os.listdir(svc_dir)):
            fpath = os.path.join(svc_dir, fname)
            if not os.path.isfile(fpath):
                continue

            if fname.endswith(".csv"):
                try:
                    with open(fpath, "r", newline="", encoding="utf-8") as f:
                        reader = _csv.DictReader(f)
                        headers = reader.fieldnames or []
                        rows = []
                        for i, row in enumerate(reader):
                            if i >= max_rows:
                                break
                            rows.append(row)
                    if headers and rows:
                        svc_lines.append("**%s** — columns: %s" % (fname, ", ".join(headers)))
                        for row in rows[:2]:
                            compact = {k: v[:60] if isinstance(v, str) and len(v) > 60
                                        else v for k, v in list(row.items())[:8]}
                            svc_lines.append("  row: %s" % json.dumps(compact, ensure_ascii=False))
                        file_count += 1
                except Exception:
                    _logger.debug("snapshot: failed to read csv %s", fpath, exc_info=True)

            elif fname.endswith(".json") and not fname.endswith("_postman_collection.json"):
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if isinstance(data, dict):
                        keys = list(data.keys())[:10]
                        svc_lines.append("**%s** — top-level keys: %s" % (fname, ", ".join(keys)))
                        for k in keys[:3]:
                            val = data[k]
                            if isinstance(val, str) and len(val) > 80:
                                val = val[:80] + "..."
                            elif isinstance(val, (list, dict)):
                                val = "%s (len=%d)" % (type(val).__name__, len(val))
                            svc_lines.append("  %s: %s" % (k, val))
                    elif isinstance(data, list) and data:
                        svc_lines.append("**%s** — array of %d items" % (fname, len(data)))
                        if isinstance(data[0], dict):
                            svc_lines.append("  sample keys: %s" % ", ".join(list(data[0].keys())[:8]))
                    file_count += 1
                except Exception:
                    _logger.debug("snapshot: failed to read json %s", fpath, exc_info=True)

        if file_count > 0:
            snapshot_parts.append("\n".join(svc_lines))

    if not snapshot_parts:
        return ""

    header = (
        "Below is a snapshot of the actual mock data files that each API service "
        "serves. Use these REAL entity IDs, field names, and values when writing "
        "assertions. Do NOT invent IDs or values — use the ones shown here or "
        "check via API calls in your tests.\n"
    )
    return header + "\n\n" + "\n\n".join(snapshot_parts)
