"""Shared helpers for mock-API tests and the one-shot diagnostic tool.

Source of truth for: discovering APIs, loading each server.py without
collisions, harvesting candidate IDs from data files, listing routes,
substituting path params. Both `tools/check_all_mocks.py` and
`tests/mocks/test_*.py` import from here.

Layout invariant: every `environment/<name>-api/server.py` imports
`tracking_middleware` and a sibling data module as siblings, so we must
prepend BOTH the api dir AND `environment/` to sys.path before import.
"""
from __future__ import annotations

import csv
import importlib.util
import io
import json
import re
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any, Callable, Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_DIR = REPO_ROOT / "environment"

GENERIC_FALLBACKS = ["1", "test", "abc123", "default"]


def discover_api_dirs() -> list[Path]:
    return sorted(
        p for p in ENV_DIR.iterdir()
        if p.is_dir() and (p / "service.toml").exists()
    )


def read_service_toml(api_dir: Path) -> dict[str, Any]:
    out: dict[str, Any] = {}
    text = (api_dir / "service.toml").read_text(encoding="utf-8")
    for line in text.splitlines():
        m = re.match(r'^\s*(\w+)\s*=\s*(.+?)\s*$', line)
        if not m:
            continue
        key, raw = m.group(1), m.group(2).strip()
        if raw.startswith('"') and raw.endswith('"'):
            raw = raw[1:-1]
        elif raw.isdigit():
            raw = int(raw)  # type: ignore[assignment]
        out[key] = raw
    return out


def looks_like_id_field(name: str) -> bool:
    n = name.lower()
    return (
        n == "id"
        or n.endswith("_id")
        or n in ("name", "slug", "key", "code", "symbol", "username", "email")
        or (n.endswith("id") and len(n) < 30)
    )


def harvest_ids(api_dir: Path) -> dict[str, list[str]]:
    pool: dict[str, list[str]] = {}

    def collect(field_name: str, value: Any) -> None:
        if value is None:
            return
        s = str(value)
        if not s or len(s) > 200:
            return
        pool.setdefault(field_name, [])
        if s not in pool[field_name]:
            pool[field_name].append(s)

    def walk_json(obj: Any) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (str, int)) and looks_like_id_field(k):
                    collect(k, v)
                walk_json(v)
        elif isinstance(obj, list):
            for item in obj:
                walk_json(item)

    for f in sorted(api_dir.iterdir()):
        if f.suffix == ".json":
            try:
                walk_json(json.loads(f.read_text(encoding="utf-8")))
            except Exception:
                continue
        elif f.suffix == ".csv":
            try:
                with f.open(encoding="utf-8") as fh:
                    reader = csv.DictReader(fh)
                    for row in reader:
                        for k, v in row.items():
                            if k and looks_like_id_field(k):
                                collect(k, v)
            except Exception:
                continue
    return pool


def substitute_path_params(path: str, pool: dict[str, list[str]]) -> str:
    def replacer(m: re.Match) -> str:
        param = m.group(1)
        candidates: list[str] = []
        if param in pool:
            candidates = pool[param]
        else:
            base = param.removesuffix("_id")
            if base in pool:
                candidates = pool[base]
            elif f"{base}_id" in pool:
                candidates = pool[f"{base}_id"]
            else:
                for k, v in pool.items():
                    if k.endswith("_id") or k == "id":
                        candidates = v
                        break
        if not candidates:
            candidates = GENERIC_FALLBACKS
        return str(candidates[0])

    return re.sub(r"\{(\w+)(?::[^}]+)?\}", replacer, path)


def load_app(api_dir: Path):
    """Import api_dir/server.py and return its FastAPI `app`.

    Each server.py imports `tracking_middleware` and `<something>_data`
    as siblings. We prepend api_dir + ENV_DIR to sys.path, capture
    stdout/err, then evict newly-loaded modules so the next API doesn't
    inherit a stale `ring_data` / `classroom_data` etc.
    """
    server_py = api_dir / "server.py"
    if not server_py.exists():
        raise FileNotFoundError(f"missing server.py: {api_dir}")

    saved_path = list(sys.path)
    saved_mods = dict(sys.modules)
    sys.path[:0] = [str(api_dir), str(ENV_DIR)]

    buf_out, buf_err = io.StringIO(), io.StringIO()
    try:
        with redirect_stdout(buf_out), redirect_stderr(buf_err):
            spec = importlib.util.spec_from_file_location(
                f"_mock_{api_dir.name.replace('-', '_')}_server",
                str(server_py),
            )
            assert spec is not None and spec.loader is not None
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        return mod.app
    finally:
        sys.path[:] = saved_path
        for k in list(sys.modules):
            if k not in saved_mods:
                del sys.modules[k]


def list_routes(app) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for route in app.routes:
        methods = getattr(route, "methods", None)
        path = getattr(route, "path", None)
        if not methods or not path:
            continue
        for m in methods:
            if m == "HEAD":
                continue
            out.append((m, path))
    return out


def iter_data_files(api_dir: Path, suffixes: Iterable[str]) -> list[Path]:
    return [
        f for f in sorted(api_dir.iterdir())
        if f.is_file() and f.suffix in suffixes
    ]


def csv_expected_column_count(path: Path) -> int:
    with path.open(encoding="utf-8", newline="") as fh:
        return len(next(csv.reader(fh)))


def csv_bad_rows(path: Path) -> list[tuple[int, int, int]]:
    """Return [(row_no, expected_cols, actual_cols), ...] for rows whose
    column count differs from the header. Row numbers are 1-indexed and
    EXCLUDE the header. Catches the unquoted-comma CSV bug class that
    crashed myfitnesspal-api on the danielle-lee_data task.
    """
    bad: list[tuple[int, int, int]] = []
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        try:
            header = next(reader)
        except StopIteration:
            return bad
        expected = len(header)
        for i, row in enumerate(reader, start=1):
            if len(row) != expected:
                bad.append((i, expected, len(row)))
    return bad
